async function loadDresses() {

    const response = await fetch('/api/dresses');
    const dresses = await response.json();

    const container = document.getElementById('dress-container');

    dresses.forEach(dress => {

        const card = document.createElement('div');
        card.className = 'card';

        card.innerHTML = `
            <img src="${dress.image_url}" />

            <div class="card-content">
                <h2>${dress.product_name}</h2>

                <p>${dress.brand}</p>

                <p class="price">$${dress.sale_price}</p>

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

    body.innerHTML = `
        <img class="detail-image" src="${dress.image_url}" />

        <h1>${dress.product_name}</h1>

        <h2>${dress.brand}</h2>

        <p class="price">Sale Price: $${dress.sale_price}</p>

        <p class="price">Full Price: $${dress.full_price}</p>

        <hr>

        <h2>Designer Information</h2>

        <p><strong>CEO:</strong> ${dress.ceo || 'N/A'}</p>

        <p><strong>Creative Director:</strong>
        ${dress.creative_director || 'N/A'}</p>

        <p><strong>Country:</strong>
        ${dress.country || 'N/A'}</p>

        <p><strong>Headquarters:</strong>
        ${dress.headquarters || 'N/A'}</p>

        <p><strong>Founded:</strong>
        ${dress.founded_year || 'N/A'}</p>
    `;

    modal.classList.remove('hidden');
}


document.getElementById('close-btn').addEventListener('click', () => {
    document.getElementById('modal').classList.add('hidden');
});


window.addEventListener('click', (event) => {
    const modal = document.getElementById('modal');

    if (event.target === modal) {
        modal.classList.add('hidden');
    }
});


loadDresses();
