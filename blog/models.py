import re

import markdown
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from mdx_math import MathExtension


def generate_rich_content(value) -> dict:
    # post = super(PostDetailView, self).get_object(queryset=None)
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        # 'markdown.extensions.toc',
        TocExtension(slugify=slugify),
        MathExtension(enable_dollar_delimiter=True),
    ])
    content = md.convert(value)
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    toc = m.group(1) if m is not None else ''

    return {
        'content': content,
        'toc': toc,
    }


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name


class Post(models.Model):
    title = models.CharField(max_length=80, verbose_name='标题')
    body = models.TextField('正文')
    create_time = models.DateTimeField('创建时间', default=timezone.now)
    modified_time = models.DateTimeField('最后修改时间')
    excerpt = models.CharField('摘要', max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    views_num = models.PositiveIntegerField(default=0, editable=False)

    def increase_views(self):
        self.views_num += 1
        self.save(update_fields=['views_num'])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.modified_time = timezone.now()
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            MathExtension(enable_dollar_delimiter=True),
        ])
        self.excerpt = strip_tags(md.convert(self.body))[:60]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # print((reverse('blog:detail', kwargs={'pk': self.pk})))
        return reverse('blog:detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-create_time', 'title']

    @cached_property
    def rich_content(self):
        return generate_rich_content(self.body)

    @property
    def toc(self):
        return self.rich_content.get("toc", "")

    @property
    def body_html(self):
        return self.rich_content.get("content", "")
