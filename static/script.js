async function loadDresses() {

    const response = await fetch('/api/dresses');
    const dresses = await response.json();

    const container = document.getElementById('dress-container');

    container.innerHTML = "";

    dresses.forEach(dress => {

        const card = document.createElement('div');
        card.className = 'card';

        // Price logic
        let priceHTML = "";

        if (
            dress.sale_price_usd &&
            dress.full_price_usd &&
            dress.sale_price_usd !== dress.full_price_usd
        ) {

            priceHTML = `
                <p class="price">
                    ${dress.sale_price_usd}
                </p>

                <p class="full-price">
                    ${dress.full_price_usd}
                </p>
            `;

        } else {

            priceHTML = `
                <p class="price">
                    ${dress.full_price_usd}
                </p>
            `;
        }

        card.innerHTML = `

            <img
                src="${dress.image_url}"
                alt="${dress.product_name}"
                class="dress-image"
            />

            <div class="card-content">

                <h2>${dress.product_name}</h2>

                <p class="brand">${dress.brand}</p>

                ${priceHTML}

                <button onclick="showDetails(${dress.id})">
                    View Details
                </button>

            </div>
        `;

        container.appendChild(card);
    });
}


async function showDetails(id) {

    const response = await fetch(`/api/dresses/${id}`);
    const dress = await response.json();

    const modal = document.getElementById('modal');
    const body = document.getElementById('modal-body');

    // Modal price logic
    let detailPriceHTML = "";

    if (
        dress.sale_price_usd &&
        dress.full_price_usd &&
        dress.sale_price_usd !== dress.full_price_usd
    ) {

        detailPriceHTML = `
            <p class="price">
                Sale Price: ${dress.sale_price_usd}
            </p>

            <p class="full-price">
                Full Price: ${dress.full_price_usd}
            </p>
        `;

    } else {

        detailPriceHTML = `
            <p class="price">
                Price: ${dress.full_price_usd}
            </p>
        `;
    }

    body.innerHTML = `

        <img
            src="${dress.image_url}"
            alt="${dress.product_name}"
            class="modal-image"
        />

        <h1>${dress.product_name}</h1>

        <h2>${dress.brand}</h2>

        ${detailPriceHTML}

        <hr>

        <h2>Designer Information</h2>

        <p>
            <strong>CEO:</strong>
            ${dress.ceo || 'Unknown'}
        </p>

        <p>
            <strong>Creative Director:</strong>
            ${dress.creative_director || 'Unknown'}
        </p>

        <p>
            <strong>Country:</strong>
            ${dress.country || 'Unknown'}
        </p>

        <p>
            <strong>Headquarters:</strong>
            ${dress.headquarters || 'Unknown'}
        </p>

        <p>
            <strong>Founded:</strong>
            ${dress.founded_year || 'Unknown'}
        </p>
    `;

    modal.classList.remove('hidden');
}


// Close modal button
document.getElementById('close-btn').addEventListener('click', () => {

    document.getElementById('modal').classList.add('hidden');
});


// Close when clicking outside modal
window.addEventListener('click', (event) => {

    const modal = document.getElementById('modal');

    if (event.target === modal) {
        modal.classList.add('hidden');
    }
});


loadDresses();