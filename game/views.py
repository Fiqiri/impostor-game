import random
import secrets
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Player, Word

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def gen_code(n=6):
    return "".join(secrets.choice(ALPHABET) for _ in range(n))


def home(request):
    # kategoritë ekzistuese (vetëm active, jo bosh)
    categories = (
        Word.objects.filter(active=True)
        .exclude(category__isnull=True)
        .exclude(category__exact="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )
    return render(request, "game/home.html", {"categories": list(categories)})


def create_room(request):
    if request.method != "POST":
        return redirect("home")

    raw = (request.POST.get("names") or "").strip()
    impostor_count = int(request.POST.get("impostor_count") or "1")
    chosen_category = (request.POST.get("category") or "").strip()

    names = [x.strip() for x in raw.splitlines() if x.strip()]

    # unique keep order
    seen = set()
    uniq = []
    for n in names:
        if n not in seen:
            uniq.append(n)
            seen.add(n)

    if not (4 <= len(uniq) <= 8):
        return HttpResponseBadRequest("Duhet 4 deri 8 lojtarë.")
    if impostor_count not in (1, 2):
        return HttpResponseBadRequest("Impostor_count duhet 1 ose 2.")
    if impostor_count >= len(uniq):
        return HttpResponseBadRequest("Impostorët s’mund të jenë sa lojtarët.")

    # Merr fjalën nga kategoria (nëse u zgjodh), përndryshe random nga të gjitha
    qs = Word.objects.filter(active=True)
    if chosen_category:
        qs = qs.filter(category=chosen_category)

    word_obj = qs.order_by("?").first()

    # fallback nëse kategoria s'ka fjalë
    if not word_obj:
        word_obj = Word.objects.filter(active=True).order_by("?").first()

    if not word_obj:
        return HttpResponseBadRequest("Nuk ka fjalë aktive në DB. Importo fjalët ose shto te /admin.")

    code = gen_code()
    while Room.objects.filter(code=code).exists():
        code = gen_code()

    room = Room.objects.create(
        code=code,
        impostor_count=impostor_count,
        word=word_obj.text,
        category=word_obj.category or None,
    )

    # random order = radha e zbulimit
    order = uniq[:]
    random.shuffle(order)

    impostor_indices = set(random.sample(range(len(order)), impostor_count))
    for i, name in enumerate(order):
        Player.objects.create(room=room, name=name, is_impostor=(i in impostor_indices))

    # Kush fillon (del vetëm në fund)
    room.starter_name = random.choice(order)
    room.save(update_fields=["starter_name"])

    return redirect("handoff", code=room.code)


def handoff(request, code: str):
    room = get_object_or_404(Room, code=code)
    players = list(room.players.all().order_by("id"))

    if room.reveal_index >= len(players):
        return redirect("done", code=room.code)

    current = players[room.reveal_index]
    return render(request, "game/handoff.html", {"room": room, "current": current})


def reveal(request, code: str):
    room = get_object_or_404(Room, code=code)
    players = list(room.players.all().order_by("id"))

    if room.reveal_index >= len(players):
        return redirect("done", code=room.code)

    current = players[room.reveal_index]
    show_word = not current.is_impostor  # vetëm crew e sheh fjalën

    return render(request, "game/reveal.html", {"room": room, "current": current, "show_word": show_word})


def next_player(request, code: str):
    if request.method != "POST":
        return redirect("handoff", code=code)

    room = get_object_or_404(Room, code=code)
    total = room.players.count()

    room.reveal_index += 1
    room.save(update_fields=["reveal_index"])

    if room.reveal_index >= total:
        return redirect("done", code=room.code)

    return redirect("handoff", code=room.code)


def done(request, code: str):
    room = get_object_or_404(Room, code=code)
    impostors = list(room.players.filter(is_impostor=True).values_list("name", flat=True))
    return render(request, "game/done.html", {"room": room, "impostors": impostors})
