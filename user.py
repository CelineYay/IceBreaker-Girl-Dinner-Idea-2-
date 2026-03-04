from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import torch
import PyPDF2
import os
import numpy as np


from app_and_db import db


class User(db.Model, UserMixin):
    """
    User class
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    phone_number = db.Column(db.String(300), nullable=False)
    linkedin_path = db.Column(db.String(300))
    linkedin_embedding = db.Column(db.JSON)
    email = db.Column(db.String(300), nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)

    def __init__(self, name, phone_number, linkedin_path, linkedin_embedding, email, password_hash):
        self.name = name
        self.phone_number = phone_number
        self.linkedin_path = linkedin_path
        self.linkedin_embedding = linkedin_embedding
        self.email = email
        self.password_hash = password_hash

    def set_embedding(self, embedding_tensor):
        if isinstance(embedding_tensor, torch.Tensor):
            self.linkedin_embedding = embedding_tensor.tolist()
        else:
            self.linkedin_embedding = embedding_tensor

    def get_embedding_tensor(self):
        if self.linkedin_embedding:
            return torch.tensor(self.linkedin_embedding)
        return None

    def __repr__(self):
        return '<User {}>'.format(self.name)


def get_linkedin_embedding_vector(linkedin_path):
    """
    This function gets an embedding vector from the resume.pdf
    :param linkedin_path: path to the resume/linkedin
    :return: list, string
    """
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

    if not os.path.exists(linkedin_path):
        raise FileNotFoundError(f"PDF file not found at path: {linkedin_path}")

    if not linkedin_path.lower().endswith('.pdf'):
        raise ValueError(f"File must be a PDF. Got: {linkedin_path}")

    text = ""
    try:
        with open(linkedin_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                text += page_text + "\n"
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")

    if not text.strip():
        raise ValueError("No text could be extracted from the PDF. The file might be scanned or image-based.")

    text = ' '.join(text.split())

    with torch.no_grad():
        embedding = model.encode(text)

        if isinstance(embedding, torch.Tensor):
            embedding_list = embedding.tolist()
        elif isinstance(embedding, np.ndarray):
            embedding_list = embedding.tolist()
        else:
            embedding_list = embedding

    return embedding_list, text


def create_user(name, phone_number, email, password, linkedin_path=""):
    """
    This function adds a new user to the database
    :param name: name
    :param phone_number: phone_number
    :param email: email
    :param linkedin_path: linkedin_path
    :param password: password
    :return: None
    """
    resume_embedding_list, _ = get_linkedin_embedding_vector(linkedin_path)
    new_user = User(
        name=name,
        phone_number=phone_number,
        email=email,
        linkedin_path=linkedin_path,
        linkedin_embedding=resume_embedding_list,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()


def get_user_by_email(email):
    """
    This function finds the user by email
    :param email: email
    :return: None
    """
    return User.query.filter_by(email=email).first()


def get_user_by_id(id):
    """
    This function finds the user by id
    :param id: id
    :return: None
    """
    return User.query.filter_by(id=id).first()


def check_password(user, password):
    """
    This function checks whether the password is correct
    :param user: user
    :param password: password
    :return: Bool
    """
    return check_password_hash(user.password_hash, password)
