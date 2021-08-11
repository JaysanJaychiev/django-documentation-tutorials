import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from . models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        был недавно опубликован возвращает значение 
        False для вопросов, дата публикации которых
        в будущем.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently () возвращает False для вопросов, для которых pub_date
        старше 1 дня.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently () возвращает True для вопросов, для которых pub_date
         находится в течение последнего дня.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Создайте вопрос с заданным `question_text` и опубликуйте
    смещение заданного количества дней до настоящего момента (отрицательное 
    для опубликованных вопросов
    в прошлом положительно для вопросов, которые еще не были опубликованы).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)



class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """
        если вопросов нет, отображается соответствующее сообщение.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are availale.')
        self.assertQuerysetEqual(response.context['latest_question_list'],
        [])

    def test_past_question(self):
        """
        Вопросы с pub_date в прошлом отображаются в
        индексная страница.
        """
        question = create_question(question_text="Past question.",
        days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Вопросы с pub_date в будущем не отображаются в
        индексную страницу.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'],
        [])

    def test_future_question_and_past_question(self):
        """
        Даже если существуют и прошлый, и будущий вопрос, только прошлые 
        вопросы отображаются.
        """
        question = create_question(question_text="Past question.", days=30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_question(self):
        """
        На странице указателя вопросов может отображаться несколько вопросов.
        """
        question1 = create_question(question_text="Past question 1.", 
    days=-30)
        question2 = create_question(question_text="Past question 2.", 
    days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        Подробное представление вопроса с pub_date в будущем
        возвращает ошибку 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        Подробное представление вопроса с pub_date в прошлом
        отображает текст вопроса.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)