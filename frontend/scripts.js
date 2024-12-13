const BASE_URL = 'http://127.0.0.1:9991/path-hash/';

const createColumn = (content, size = 4) => {
    let col = document.createElement('div');
    col.classList.add(`col-${size}`, 'border');
    content instanceof Element ? col.appendChild(content) : col.innerText = content;
    return col
}

const makeLink = (url) => {
    let a = document.createElement('a');
    a.href = 'http://' + url;
    a.textContent = url;
    return a
}

const createInstanceRow = (instance) => {
    let row = document.createElement('div');
    row.classList.add('row', 'justify-content-center', 'text-center');
    row.appendChild(createColumn(makeLink(`${instance.public_ip}:8080`)));
    row.appendChild(createColumn(instance.name));
    row.appendChild(createColumn('WIP: button DELETE'));
    return row
}

const appendInstanceRows = (rows) => {
    let table = document.getElementById('instancesTable');
    table.replaceChildren(...rows);
}

const listInstances = () => {
    let url = BASE_URL + 'vms/';  // Replace with your URL

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
    })
        .then(response => response.json())  // Parses the JSON response
        .then(data => {
            let instanceRows = data.map(instance => createInstanceRow(instance));
            appendInstanceRows(instanceRows);
        })
        .catch(error => console.error('Error:', error));
};

const collectFormData = () => {
    let form = document.getElementById('creationForm');
    return new FormData(form);
};

const createInstance = () => {
    let formData = collectFormData();

    let url = BASE_URL + 'vms/';  // Replace with your URL

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        body: JSON.stringify({
            python_envs: formData.getAll('python'),
            repo_urls: formData.getAll('customRepo'),
            size: formData.get('size')
        })
    })
        .then(response => response.json())  // Parses the JSON response
        .then(data => {
            listInstances();
        })
        .catch(error => console.error('Error:', error));
};

const repoValidationReset = () => {
    let button = document.getElementById('check');
    if (!button.classList.contains('btn-primary')) {
        button.classList.remove(...button.classList);
        button.classList.add('btn', 'btn-primary')
        button.innerText = 'Check Repository';
        button.disabled = false;
    }
};

const repoValidationSuccess = () => {
    let button = document.getElementById('check');
    button.classList.replace('btn-primary', 'btn-outline-success');
    button.innerText = 'Valid Repository ✅';
    button.disabled = true;
};

const repoValidationFail = () => {
    let button = document.getElementById('check');
    button.classList.replace('btn-primary', 'btn-outline-danger');
    button.innerText = 'Invalid Repository ❌';
    button.disabled = true;
};

const checkCustomRepo = () => {
    let formData = collectFormData();

    let url = BASE_URL + 'repos/validate/' + formData.get('customRepo');

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
    })
        .then(response => response.json())  // Parses the JSON response
        .then(data => data.message === 'Valid' ? repoValidationSuccess() : repoValidationFail())
        .catch(error => console.error('Error:', error));
}

const controlCollapse = () => {
    let instanceListTable = document.getElementById('instanceListTable');
    let instanceCreationForm = document.getElementById('instanceCreationForm');

    let instanceListTableCollapse = new bootstrap.Collapse(instanceListTable, {toggle: false});
    let instanceCreationFormCollapse = new bootstrap.Collapse(instanceCreationForm, {toggle: false});

    instanceListTable.addEventListener('show.bs.collapse', event => instanceCreationFormCollapse.hide());
    instanceCreationForm.addEventListener('show.bs.collapse', event => instanceListTableCollapse.hide());
}


document.getElementById('instanceListTable').addEventListener('shown.bs.collapse', listInstances);
document.getElementById('launch').addEventListener('click', createInstance);
document.getElementById('check').addEventListener('click', checkCustomRepo);
document.getElementById('customRepo').addEventListener('change', repoValidationReset);
document.getElementById('refresh').addEventListener('click', listInstances);
controlCollapse();
