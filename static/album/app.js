const slotTimers = new WeakMap();

function updateSlot(slot, quantidade) {
    slot.classList.toggle('album-slot-owned', quantidade > 0);

    let badge = slot.querySelector('.album-slot-badge');
    if (quantidade > 0) {
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'album-slot-badge';
            slot.prepend(badge);
        }
        badge.textContent = quantidade;
    } else if (badge) {
        badge.remove();
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
