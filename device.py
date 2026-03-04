from app_and_db import db, app
from user import User


class Device(db.Model):
    """
    Exhibition class
    """
    id = db.Column(db.Integer, primary_key=True)
    rfid = db.Column(db.String(300), nullable=False)
    owner_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(300), nullable=False)

    def __init__(self, rfid, owner_id, name):
        self.rfid = rfid
        self.owner_id = owner_id
        self.name = name

    def __repr__(self):
        return '<Device {}>'.format(self.name)


def add_device(rfid, owner_id, name="Link Sling"):
    """
    This function adds a new device to the database
    :param rfid: rfid
    :param owner_id: owner_id
    :param name: name
    :return: None
    """
    new_device = Device(rfid=rfid, owner_id=owner_id, name=name)
    db.session.add(new_device)
    db.session.commit()


def get_user_by_device_rfid(rfid):
    """
    This function finds the user by their device
    :param rfid: rfid
    :return: User
    """
    device = Device.query.filter_by(rfid=rfid).first()
    return User.query.filter_by(id=device.owner_id).first()


def get_devices_by_user(user):
    """
    This function finds all the user's devices
    :param user: User
    :return: list of items of the class Device
    """
    return Device.query.filter_by(owner_id=user.id).all()


def get_device_by_device_id(device_id):
    """
    Deletes the device by its id
    :param device_id: device_id
    :return: Device
    """
    return Device.query.filter_by(id=device_id).first()


def delete_device_by_device_id(device_id):
    """
    Deletes the device by its id
    :param device_id: device_id
    :return: None
    """
    with app.app_context():
        device = Device.query.filter_by(id=device_id).first()
        db.session.delete(device)
        db.session.commit()
