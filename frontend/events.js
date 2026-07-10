// =============================================
// events.js — Narrative event engine
// =============================================

export function checkNarrativeEvents(day, scenario, seed) {
    const modifiers = { buyBoost: 0, rejectBoost: 0 };
    const product = scenario.product_name?.value || 'the product';
    const category = scenario.category?.value || 'Technology';
    const region = scenario.launch_region?.value || 'the market';
    const price = Number(scenario.price?.value) || 100;

    const events = getEventsForSeed(seed, day, product, category, region, price);
    events.forEach(evt => {
        modifiers.buyBoost += (evt.buyBoost || 0);
        modifiers.rejectBoost += (evt.rejectBoost || 0);
        emitEvent(day, evt.message, evt.type);
    });

    return modifiers;
}

function getEventsForSeed(seed, day, product, category, region, price) {
    const r = (offset) => {
        let s = (seed ^ (offset * 2654435761)) >>> 0;
        s ^= s << 13; s ^= s >> 17; s ^= s << 5;
        return (s >>> 0) / 4294967296;
    };

    const events = [];

    // Day 3: Influencer review
    if (day === 3) {
        const positive = r(3) > 0.4;
        events.push({
            message: positive
                ? `Major ${category} influencer publishes a rave review of ${product}. Demand spikes.`
                : `Micro-influencer posts mixed review of ${product}. Moderate initial buzz.`,
            type: positive ? 'positive' : 'neutral',
            buyBoost: positive ? 2.0 : 0.5,
        });
    }

    // Day 7: Competitor response
    if (day === 7) {
        const fierce = r(7) > 0.5;
        events.push({
            message: fierce
                ? `Top competitor in ${region} announces a 20% price cut. Adoption pressure increases.`
                : `Competitors begin monitoring ${product}. No counter-move yet.`,
            type: fierce ? 'negative' : 'neutral',
            rejectBoost: fierce ? 1.5 : 0.3,
        });
    }

    // Day 12–14: Mid-campaign push
    if (day === 12) {
        events.push({
            message: `Paid media campaign reaches peak delivery. ${product} trending on social platforms in ${region}.`,
            type: 'positive',
            buyBoost: 1.5,
        });
    }

    // Day 17: Macro event
    if (day === 17) {
        const inflation = r(17) > 0.5;
        events.push({
            message: inflation
                ? `Consumer confidence index drops 3 points in ${region}. Budget-conscious buyers delay decision.`
                : `Regional employment numbers beat expectations. Consumer spending outlook improves.`,
            type: inflation ? 'negative' : 'positive',
            rejectBoost: inflation ? 1.5 : 0,
            buyBoost: inflation ? 0 : 1.0,
        });
    }

    // Day 22: Viral moment
    if (day === 22) {
        const viral = r(22) > 0.3;
        if (viral) {
            events.push({
                message: `${product} goes viral on social media. Celebrity shares unboxing video. Demand surges.`,
                type: 'positive',
                buyBoost: 2.5,
            });
        }
    }

    // Day 27: End-of-month paycheck
    if (day === 27) {
        events.push({
            message: `End-of-month salary cycle — consumer purchasing power at monthly peak. Adoption accelerates.`,
            type: 'positive',
            buyBoost: 1.0,
        });
    }

    return events;
}

function emitEvent(day, message, type = 'positive') {
    const list = document.getElementById('timeline-events-list');
    if (list) {
        const li = document.createElement('li');
        const dotColor = type === 'positive' ? 'bg-success' : type === 'negative' ? 'bg-danger' : 'bg-warning';
        li.className = 'flex gap-2 items-start text-[11px] leading-snug opacity-0';
        li.style.transition = 'opacity 0.4s ease';
        li.innerHTML = `<span class="w-1.5 h-1.5 rounded-full ${dotColor} mt-1.5 shrink-0"></span><span><span class="text-muted font-medium">Day ${day}:</span> <span class="text-gray-300">${message}</span></span>`;
        list.appendChild(li);
        list.scrollTop = list.scrollHeight;
        requestAnimationFrame(() => { li.style.opacity = '1'; });
    }
    document.dispatchEvent(new CustomEvent('narrative-event', { detail: { day, message, type } }));
}
