from python_meetupbot.models import Users, Events
from .keyboard_utils import make_choose_keyboard, make_speaker_keyboard, make_guest_keyboard
import uuid
from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters
from python_meetupbot.models import Users, Speakers, Topics, Questions, Comments, Events, Eventcomments
from python_meetupbot.handlers.meetup import static_text
from datetime import datetime


GUEST_OPTIONS, ASK_QUESTION, LEAVE_FEEDBACK_TALK, LEAVE_FEEDBACK_EVENT, CREATE_MEETUP, OPTION, MEETUP_END_TIME, MEETUP_DATE, MEETUP_START_TIME = range(9)


def test(update: Update, _):
    pass


def guest_options(update: Update, _: CallbackContext):
    update.message.reply_text(static_text.choose_option, reply_markup=make_guest_keyboard())
    return GUEST_OPTIONS


def handle_guest_option(update: Update, _: CallbackContext):
    option = update.message.text

    if option == static_text.guest_options_buttons[0]:
        show_events_schedule(update, _)

    elif option == static_text.guest_options_buttons[1]:
        update.message.reply_text(static_text.ask_question_text)
        return ASK_QUESTION

    elif option == static_text.guest_options_buttons[2]:
        update.message.reply_text(static_text.leave_feedback_talk_text)
        return LEAVE_FEEDBACK_TALK

    elif option == static_text.guest_options_buttons[3]:
        update.message.reply_text(static_text.leave_feedback_event_text)
        return LEAVE_FEEDBACK_EVENT

    return ConversationHandler.END


def ask_question(update: Update, _):
    question_text = update.message.text
    Questions.objects.create(
        telegram_id=update.message.from_user.id,
        date=Events.objects.get(date=datetime.now().date()),
        speaker_id=None,
        question=question_text
    )
    update.message.reply_text(static_text.question_sent)
    return ConversationHandler.END


def leave_feedback_talk(update: Update, _):
    feedback_text = update.message.text
    Comments.objects.create(
        telegram_id=update.message.from_user.id,
        date=Events.objects.get(date=datetime.now().date()),
        speaker_id=None,
        comment=feedback_text
    )
    update.message.reply_text(static_text.feedback_talk_sent)
    return ConversationHandler.END


def leave_feedback_event(update: Update, _):
    feedback_text = update.message.text
    Eventcomments.objects.create(
        telegram_id=update.message.from_user.id,
        date=Events.objects.get(date=datetime.now().date()),
        meetup_comment=feedback_text
    )
    update.message.reply_text(static_text.feedback_event_sent)
    return ConversationHandler.END


def show_events_schedule(update: Update, _):
    events = Events.objects.all().order_by('date')

    if not events:
        update.message.reply_text(static_text.no_events)
        return ConversationHandler.END

    response = static_text.events_schedule_header
    for event in events:
        response += f"{static_text.event_date}: {event.date}\n"
        response += f"{static_text.event_start}: {event.start}\n"
        response += f"{static_text.event_end}: {event.end}\n"
        response += "\n"

    update.message.reply_text(response)
    return ConversationHandler.END


def get_speaker_commands(update: Update, _):
    speaker = Users.objects.get(telegram_id=update.message.from_user.id)
    if Speakers.objects.filter(telegram_id=speaker) is None:
        update.message.reply_text(static_text.only_for_speakers)
        return ConversationHandler.END
    text = static_text.speaker_text
    update.message.reply_text(text=text,
                              reply_markup=make_speaker_keyboard())


def exit(update, _):
    first_name = update.message.from_user.first_name
    text = static_text.bye_bye.format(
        first_name=first_name
    )
    update.message.reply_text(text=text)
    return ConversationHandler.END


def create_meetup(update: Update, meetup_description):
    print('create_meetup')
    meetup_description.bot_data['meetup_name'] = update.message.text
    text = static_text.meetup_date
    update.message.reply_text(
        text=text
    )
    return MEETUP_DATE


def meetup_date(update: Update, meetup_description):
    print('meetup_date')
    meetup_description.bot_data['meetup_date'] = update.message.text
    text = static_text.meetup_start_time
    update.message.reply_text(
        text=text
    )
    return MEETUP_START_TIME


def meetup_start_time(update: Update, meetup_description):
    print('meetup_start_time')
    print(update.message.text)
    meetup_description.bot_data['meetup_start_time'] = update.message.text
    text = static_text.meetup_end_time
    update.message.reply_text(
        text=text
    )
    return MEETUP_END_TIME


def meetup_end_time(update: Update, meetup_description):
    print('meetup_end_time')
    meetup_description.bot_data['meetup_end_time'] = update.message.text
    event = Events(name=meetup_description.bot_data['meetup_name'],
                   date=meetup_description.bot_data['meetup_date'],
                   start=meetup_description.bot_data['meetup_start_time'],
                   end=meetup_description.bot_data['meetup_end_time']
                   )
    event.save()
    text = static_text.meetup_created
    update.message.reply_text(
        text=text
    )


def choose_admin_button(update: Update, _):
    print('choose_admin_button')
    answer = update.message.text
    if static_text.features_choose.index(answer) == 0:
        text = static_text.meetup_name
        update.message.reply_text(
            text=text
        )
        return CREATE_MEETUP
    elif static_text.features_choose.index(answer) == 1:
        pass
    else:
        pass


def organization_option(update: Update, _):
    print('organization_option')
    user = Users.objects.get(telegram_id=update.message.from_user.id)
    if not user.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return ConversationHandler.END
    text = static_text.admin_features

    update.message.reply_text(text=text,
                              reply_markup=make_choose_keyboard())
    return OPTION
