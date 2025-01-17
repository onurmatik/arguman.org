from uuid import uuid4
import re
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.template.defaultfilters import slugify
from functools import partialmethod
from django.utils.translation import ugettext_lazy as _, get_language
from i18n.utils import normalize_language_code

from nouns.utils import get_synsets, get_lemmas, from_lemma


CONSONANT_SOUND = re.compile(r'''one(![ir])''', re.IGNORECASE|re.VERBOSE)
VOWEL_SOUND = re.compile(r'''[aeio]|u([aeiou]|[^n][^aeiou]|ni[^dmnl]|nil[^l])|h(ier|onest|onou?r|ors\b|our(!i))|[fhlmnrsx]\b''', re.IGNORECASE|re.VERBOSE)


class Noun(models.Model):
    text = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, blank=True)
    language = models.CharField(max_length=25)
    is_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("text", "language"),)

    def __str__(self):
        return self.text.title()

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.text)
            duplications = Noun.objects.filter(slug=slug,
                                               language=self.language)
            if duplications.exists():
                self.slug = "%s-%s" % (slug, uuid4().hex)
            else:
                self.slug = slug
        return super(Noun, self).save(*args, **kwargs)

    @classmethod
    def from_synset(cls, synset):
        lemmas = synset.lemma_names()
        text = lemmas[0]
        keywords = lemmas[1:]
        noun, created = cls.objects.get_or_create(
            text=from_lemma(text),
            defaults={
                'is_active': False,
                'language': normalize_language_code(get_language())
            })
        for keyword in keywords:
            noun.add_keyword(from_lemma(keyword))
        return noun

    def update_with_wordnet(self, update_antonyms=True):
        synsets = get_synsets(self.text)

        if not synsets:
            return

        for synset in synsets:
            path = synset.hypernym_paths()[0]
            parents = path[:-1]
            parent = self
            for hypernym in reversed(parents):
                noun = Noun.from_synset(hypernym)
                parent.add_hypernym(noun)
                parent = noun

            for holonym in synset.part_holonyms():
                noun = Noun.from_synset(holonym)
                self.add_holonym(noun)

            for holonym in synset.member_holonyms():
                noun = Noun.from_synset(holonym)
                self.add_holonym(noun)

        for lemma in get_lemmas(self.text):
            if lemma != self.text:
                self.add_keyword(lemma)

        if not update_antonyms:
            return

        for synset in synsets:
            for lemma in synset.lemmas():
                for antonym in lemma.antonyms():
                    noun = Noun.from_synset(antonym.synset())
                    self.add_antonym(noun)
                    noun.update_with_wordnet(update_antonyms=False)

    def add_keyword(self, text):
        keyword, created = self.keywords.get_or_create(text=text)
        return keyword

    def active_keywords(self):
        return self.keywords.filter(is_active=True)

    def active_contentions(self):
        language = normalize_language_code(get_language())
        return self.contentions.filter(
            is_published=True,
            language=language
        ).order_by('?')

    def indirect_contentions(self):
        from premises.models import Contention  # to avoid circular import
        language = normalize_language_code(get_language())
        nouns = self.out_relations.values_list('target', flat=True)
        return Contention.objects.filter(
            language=language,
            is_published=True,
            nouns__in=nouns
        ).order_by('?')

    def get_absolute_url(self):
        return reverse('nouns_detail', args=[self.slug])

    def serialize(self):
        return {
            'title': self.text,
            'absolute_url': self.get_absolute_url()
        }

    def hypernyms(self):
        return self.out_relations.filter(relation_type='hypernym')

    def hyponyms(self):
        return self.in_relations.filter(relation_type='hypernym')

    def add_relation(self, target, relation_type=None):
        relation, created = (
            self.out_relations.get_or_create(
                target=target, relation_type=relation_type)
        )
        return relation

    add_hypernym = partialmethod(add_relation, relation_type="hypernym")
    add_holonym = partialmethod(add_relation, relation_type="holonym")
    add_antonym = partialmethod(add_relation, relation_type="antonym")


class Keyword(models.Model):
    """
    Keywords for matching contentions.
    """
    noun = models.ForeignKey(Noun, related_name="keywords", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.text


class Relation(models.Model):
    """
    Holds the relationships of contentions.

        - is a (hypernym)
        - part of (holonym)
        - opposite (antonym)
        - same_as (synonym)

    """
    HYPERNYM = "hypernym"
    HOLONYM = "holonym"
    ANTONYM = "antonym"
    HYPONYM = "hyponym"
    MERONYM = "meronym"

    TYPES = (
        (HYPERNYM, _('is a')),
        (HOLONYM, _('part of')),
        (ANTONYM, _('opposite with')),
    )

    source = models.ForeignKey(Noun, related_name="out_relations", on_delete=models.CASCADE)
    target = models.ForeignKey(Noun, related_name="in_relations", on_delete=models.CASCADE)
    relation_type = models.CharField(max_length=25, choices=TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return smart_unicode(self.relation_type)

    def reverse_type(self):
        return {
            Relation.HYPERNYM: Relation.HYPONYM,
            Relation.HOLONYM: Relation.MERONYM,
            Relation.ANTONYM: Relation.ANTONYM
        }.get(self.relation_type)

    def get_reverse_type_display(self):
        return {
            Relation.HYPONYM: _("whole of"),
            Relation.MERONYM: _("whole of"),
            Relation.ANTONYM: _("opposite with")
        }.get(self.reverse_type())

    def relation_type_label(self):
        if (self.relation_type == Relation.HYPERNYM
                and self.target.language == 'en'):
            text = unicode(self.target)
            return ('is an' if not CONSONANT_SOUND.match(text)
                               and VOWEL_SOUND.match(text)
                    else 'is a')
        return self.get_relation_type_display()


class Channel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    nouns = models.ManyToManyField('Noun', blank=True)
    order = models.IntegerField()
    language = models.CharField(max_length=255, blank=True, null=True)
    is_featured = models.BooleanField(max_length=255, default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.text)
            self.slug = slug
        return super(Channel, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('channel_detail', args=[self.slug])

    def serialize(self):
        return {
            'title': self.title,
            'absolute_url': self.get_absolute_url()
        }
