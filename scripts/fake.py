import os
import pathlib
import random
import sys
from datetime import timedelta

import django
import faker
from django.utils import timezone

# 只是导入一些会用到的模块，然后通过脚本所在文件找到项目根目录
back = os.path.dirname
BASE_DIR = back(back(os.path.abspath(__file__)))

sys.path.append(BASE_DIR) # 将根目录添加到 Python 的模块搜索路径中

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogproject.settings.local')
    django.setup()

    from blog.models import Category, Post, Tag
    from comments.models import Comment
    from django.contrib.auth.models import User

    # 清空数据库中的信息
    print('Clean database')
    Post.objects.all().delete()
    Category.objects.all().delete()
    Tag.objects.all().delete()
    Comment.objects.all().delete()
    User.objects.all().delete()

    print('Create a blog superuser')
    user = User.objects.create_superuser('admin', 'admin@github.com', 'admin')

    category_list = ['ACM', 'Python', 'Django', 'Nginx', 'algorithm', 'C++', 'Docker', 'JAVA', 'HTML', "css"]
    tags_list = ['django', 'Python', 'Pipenv', 'Docker', 'Nginx', 'Elasticsearch', 'Gunicorn', 'Supervisor', 'test tag', '题解', 'std', 'nodejs', 'jsp']
    a_year_ago = timezone.now() - timedelta(days=365)

    print('Create categories and  tags')
    for cate in category_list:
        Category.objects.create(name=cate)

    for tag in tags_list:
        Tag.objects.create(name=tag)

    print('Create a Markdown sample post')
    Post.objects.create(
        title='Markdown 与代码高亮测试',
        body=pathlib.Path(BASE_DIR).joinpath('scripts', 'md.sample').read_text(encoding='utf-8'),
        category=Category.objects.create(name='Markdown测试'),
        author=user
    )

    print('Create some faked posts published within the past year')
    fake = faker.Faker()  # English
    for _ in range(100):
        tags = Tag.objects.order_by('?')
        tag1 = tags.first()
        tag2 = tags.last()
        cate = Category.objects.order_by('?').first()
        create_time = fake.date_time_between(start_date='-1y', end_date="now",
                                              tzinfo=timezone.get_current_timezone())
        post = Post.objects.create(
            title=fake.sentence().rstrip('.'),
            body='\n\n'.join(fake.paragraphs(10)),
            create_time=create_time,
            category=cate,
            author=user,
        )
        post.tags.add(tag1, tag2)
        post.save()

    fake = faker.Faker('zh_CN')
    for _ in range(100):  # Chinese
        tags = Tag.objects.order_by('?')
        tag1 = tags.first()
        tag2 = tags.last()
        cate = Category.objects.order_by('?').first()
        created_time = fake.date_time_between(start_date='-1y', end_date="now",
                                              tzinfo=timezone.get_current_timezone())
        post = Post.objects.create(
            title=fake.sentence().rstrip('.'),
            body='\n\n'.join(fake.paragraphs(10)),
            create_time=create_time,
            category=cate,
            author=user,
        )
        post.tags.add(tag1, tag2)
        post.save()

    print('Create some comments')
    for post in Post.objects.all()[:20]:
        post_created_time = post.create_time
        delta_in_days = '-' + str((timezone.now() - post_created_time).days) + 'd'
        for _ in range(random.randrange(3, 17)):
            Comment.objects.create(
                name = fake.name(),
                email=fake.email(),
                url=fake.uri(),
                text=fake.paragraph(),
                created_time=fake.date_time_between(
                    start_date=delta_in_days,
                    end_date="now",
                    tzinfo=timezone.get_current_timezone()),
                post = post,
            )
    print('Done!')
