from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import joinedload, subqueryload

from applications.notifications.models import *
import applications.users.dal as db_users
from graphspace.wrappers import with_session


@with_session
def add_owner_notification(db_session, message, type, resource, resource_id, owner_email=None, is_read=False, is_email_sent=False):
    """
    Add a new owner notification.

    :param db_session: Database session.
    :param message: Message of the notification.
    :param type: Type of the notification.
    :param resource: Resource type (graph,layout,group) of this notification.
    :param resource_id: Resource ID the notification is related to.
    :param owner_email: Email of the notification's owner.
    :param is_read: Check if notification is read or not.
    :param is_email_sent: Check if email has been sent for the notification or not.
    :return: OwnerNotification
    """
    notify = OwnerNotification(message=message, type=type, resource=resource, resource_id=resource_id,
                               owner_email=owner_email, is_read=is_read, is_email_sent=is_email_sent)
    db_session.add(notify)
    return notify


@with_session
def add_group_notification(db_session, message, type, resource, resource_id, group_id, is_read=False, is_email_sent=False):
    """
    Add a new group notification.

    :param db_session: Database session.
    :param message: Message of the notification.
    :param type: Type of the notification.
    :param resource: Resource type (graph,layout,group) of this notification.
    :param resource_id: Resource ID the notification is related to.
    :param group_id: ID of the notification's group.
    :param is_read: Check if notification is read or not.
    :param is_email_sent: Check if email has been sent for the notification or not.
    :return: list of GroupNotification
    """

    group_members = db_users.get_users_by_group(
        db_session=db_session, group_id=group_id)

    notify = []
    for mem in group_members:
        notify.append(GroupNotification(message=message, type=type, resource=resource, resource_id=resource_id,
                                        member_email=mem.email, group_id=group_id, is_read=is_read, is_email_sent=is_email_sent))
    db_session.bulk_save_objects(notify)
    return notify


@with_session
def find_owner_notifications(db_session, owner_email, is_read, limit, offset, order_by=asc(OwnerNotification.created_at)):
    query = db_session.query(OwnerNotification)

    if order_by is not None:
        query = query.order_by(order_by)

    if owner_email is not None:
        query = query.filter(OwnerNotification.owner_email.ilike(owner_email))

    if is_read is not None:
        query = query.filter(OwnerNotification.is_read.is_(is_read))

    total = query.count()

    if offset is not None and limit is not None:
        query = query.limit(limit).offset(offset)

    return total, query.all()


@with_session
def read_owner_notifications(db_session, owner_email, notification_id=None):
    query = db_session.query(OwnerNotification)
    query = query.filter(OwnerNotification.owner_email.ilike(owner_email))
    notify = None
    if notification_id is not None:
        query = query.filter(OwnerNotification.id == notification_id)
        notify = query.one_or_none()

    query = query.filter(OwnerNotification.is_read.is_(False))
    total = query.count()
    query = query.update({'is_read': True}, synchronize_session=False)

    return total, notify