import os
import pickle
import numpy as np
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.applications.xception import Xception, preprocess_input
from PIL import Image


# =========================================================
# Load Model & Tokenizer
# =========================================================
MODEL_PATH = os.path.join(settings.BASE_DIR, "captionapp", "models", "best_caption_model.keras")
TOKENIZER_PATH = os.path.join(settings.BASE_DIR, "captionapp", "models", "tokenizer.pkl")

try:
    model = load_model(MODEL_PATH)
except Exception as e:
    model = None
    print(f"⚠️ Error loading model: {e}")

try:
    with open(TOKENIZER_PATH, "rb") as f:
        tokenizer = pickle.load(f)
except Exception as e:
    tokenizer = None
    print(f"⚠️ Error loading tokenizer: {e}")

MAX_LENGTH = 84
feature_extractor = Xception(include_top=False, pooling="avg")


# =========================================================
# Helpers
# =========================================================
def extract_features(img_path):
    """Extract features from image using Xception."""
    try:
        img = Image.open(img_path).resize((299, 299)).convert("RGB")
        img = np.expand_dims(np.array(img), axis=0)
        img = preprocess_input(img)
        return feature_extractor.predict(img, verbose=0)
    except Exception as e:
        print(f"⚠️ Feature extraction error: {e}")
        return None


def beam_search_decode(photo, beam_width=3):
    """Beam Search decoding (best strategy)."""
    start_seq = [tokenizer.word_index.get("startseq")]
    sequences = [[start_seq, 0.0]]

    for _ in range(MAX_LENGTH):
        all_candidates = []
        for seq, score in sequences:
            if seq[-1] == tokenizer.word_index.get("endseq"):
                all_candidates.append([seq, score])
                continue

            padded_seq = pad_sequences([seq], maxlen=MAX_LENGTH, padding="post")
            yhat = model.predict([photo, padded_seq], verbose=0)[0]

            top_indices = np.argsort(yhat)[-beam_width:]
            for idx in top_indices:
                candidate = [seq + [idx], score - np.log(yhat[idx] + 1e-9)]
                all_candidates.append(candidate)

        sequences = sorted(all_candidates, key=lambda tup: tup[1])[:beam_width]

    best_seq = sequences[0][0]
    return decode_sequence(best_seq)


def decode_sequence(seq):
    """Convert token sequence to readable caption."""
    words = []
    for idx in seq:
        word = tokenizer.index_word.get(idx)
        if word is None or word == "startseq":
            continue
        if word == "endseq":
            break
        words.append(word)
    return " ".join(words)


# =========================================================
# Django Views
# =========================================================
def home(request):
    return render(request, "home.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


def dashboard(request):
    caption = None
    uploaded_img_url = None

    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        img_path = fs.path(filename)

        photo = extract_features(img_path)
        if photo is not None:
            caption = beam_search_decode(photo, beam_width=3)
        else:
            caption = "⚠️ Feature extraction failed."

        uploaded_img_url = fs.url(filename)

    return render(request, "dashboard.html", {
        "caption": caption,
        "uploaded_img_url": uploaded_img_url
    })
