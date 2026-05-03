const slotTimers = new WeakMap();

function updateSlot(slot, quantidade) {
    slot.classList.toggle('album-slot-owned', quantidade > 0);
    const repetidas = Math.max(quantidade - 1, 0);

    let check = slot.querySelector('.album-slot-check');
    if (quantidade > 0) {
        if (!check) {
            check = document.createElement('span');
            check.className = 'album-slot-check';
            check.innerHTML = '<i class="bi bi-check-lg"></i>';
            slot.prepend(check);
        }
    } else if (check) {
        check.remove();
    }

    let repeats = slot.querySelector('.album-slot-repeats');
    if (repetidas > 0) {
        if (!repeats) {
            repeats = document.createElement('span');
            repeats.className = 'album-slot-repeats';
            const mark = slot.querySelector('.album-slot-mark');
            slot.insertBefore(repeats, mark);
        }
        repeats.textContent = `Repetidas: ${repetidas}`;
    } else if (repeats) {
        repeats.remove();
    }
}

async function submitSlot(form, slot, delta) {
    const deltaInput = form.querySelector('input[name="delta"]');
    deltaInput.value = delta;

    const response = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'same-origin',
    });

    if (!response.ok) {
        form.submit();
        return;
    }

    const data = await response.json();
    updateSlot(slot, data.quantidade);
}

document.addEventListener('click', (event) => {
    const slot = event.target.closest('.album-slot');
    if (!slot) {
        return;
    }

    const form = slot.closest('form');
    if (!form) {
        return;
    }

    event.preventDefault();

    const deltaInput = form.querySelector('input[name="delta"]');
    const pendingTimer = slotTimers.get(form);

    if (pendingTimer) {
        clearTimeout(pendingTimer);
        slotTimers.delete(form);
        submitSlot(form, slot, '-1').catch(() => form.submit());
        return;
    }

    deltaInput.value = '1';
    const timer = setTimeout(() => {
        slotTimers.delete(form);
        submitSlot(form, slot, '1').catch(() => form.submit());
    }, 280);
    slotTimers.set(form, timer);
});
