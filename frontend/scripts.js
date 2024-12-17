const BASE_URL = document.URL.substring(0, document.URL.lastIndexOf('index'));

const createLoadingSpinner = () => {
    let spinner = document.createElement('span');
    spinner.classList.add('spinner-border', 'spinner-border-sm', 'mx-2');
    spinner.role = 'status';
    return spinner;
};

const createColumn = (content, column_id = null, size = 4) => {
    let col = document.createElement('div');
    col.classList.add(`col-${size}`, 'border');
    column_id ? col.id = column_id : null;
    content instanceof Element ? col.appendChild(content) : col.innerText = content;
    return col
};

const createLink = (url) => {
    let a = document.createElement('a');
    a.href = 'http://' + url;
    a.textContent = url;
    return a
};

const createText = (text) => {
    let span = document.createElement('span');
    span.textContent = text;
    span.classList.add('mx-3');
    return span
}


const createDeleteButton = (instanceID) => {
    let deleteButton = document.createElement('button');
    deleteButton.classList.add('btn', 'btn-danger', 'align-middle');
    deleteButton.innerText = 'Delete Instance';
    deleteButton.addEventListener('click', () => {
        deleteInstance(instanceID);
        deleteButton.appendChild(createLoadingSpinner());
        deleteButton.disabled = true;
    });
    return deleteButton;
};

const checkInstanceStatus = (instanceID) => {
    let url = BASE_URL + 'vms/' + instanceID + '/status';

    return fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
    })
        .then(response => response.json())
        .then(response => {
            return response.jhub
        })
        .catch(error => console.error('Error:', error));
};

const instanceReady = (instance) => {
    let ready = checkInstanceStatus(instance.id);
    let col = document.getElementById(instance.id);

    ready.then(isReady => {
        if (isReady === 'ready') {
            col.replaceChildren(...[createLink(`${instance.public_ip}:8080`)]);
        } else if (isReady === 'error') {
            col.replaceChildren(...[createText('Error ❌')]);
        } else {
            setTimeout(() => {
                instanceReady(instance);
            }, 5000);
        }
    });

};

const createInstanceRow = (instance) => {
    let row = document.createElement('div');
    row.classList.add('row', 'justify-content-center', 'text-center');
    let ip_column = createColumn(createLoadingSpinner(), instance.id)
    ip_column.appendChild(createText('JupyterHub is starting...'));
    row.appendChild(ip_column);
    row.appendChild(createColumn(instance.name));
    row.appendChild(createColumn(createDeleteButton(instance.id)));
    return row
};

const appendInstanceRows = (rows) => {
    let table = document.getElementById('instancesTable');
    table.replaceChildren(...rows);
};

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
            data.forEach(instance => {
                instanceReady(instance);
            });
        })
        .catch(error => console.error('Error:', error));
};

const collectFormData = () => {
    let form = document.getElementById('creationForm');
    return new FormData(form);
};

const instanceCreationStarting = (button) => {
    button.disabled = true;
    button.appendChild(createLoadingSpinner());
};

const instanceCreationSuccess = (button, text = 'Success ✅') => {
    button.removeChild(button.firstChild);
    button.classList.replace('btn-customized', 'btn-outline-success');
    button.innerText = text;
};

const instanceCreationFail = (button, text = 'Error ❌') => {
    button.removeChild(button.firstChild);
    button.classList.replace('btn-customized', 'btn-outline-danger');
    button.innerText = text;
};

const instanceCreationReset = (button) => {
    button.removeChild(button.firstChild);
    button.classList.remove(...button.classList);
    button.classList.add('btn', 'btn-primary', 'btn-customized', 'btn-lg');
    button.innerText = 'Create Instance';
    button.disabled = false;
}

const getCustomRepos = (formData, button) => {
    if (button.getAttribute('data-valid-repo') !== 'valid') {
        return null;
    } else {
        let repos = formData.getAll('customRepo').filter(Boolean);  // evil hack to not have [""]

        if (repos && repos.length) {
            return repos;
        } else {
            return null;
        }
    }
};

const createInstance = () => {
    let formData = collectFormData();

    let createInstanceButton = document.getElementById('launch');
    instanceCreationStarting(createInstanceButton);

    let button = document.getElementById('check');
    if (button.getAttribute('data-valid-repo') === 'invalid') {
        instanceCreationFail(createInstanceButton, 'Invalid Repository ❌');
    } else {
        let url = BASE_URL + 'vms/';  // Replace with your URL

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            body: JSON.stringify({
                python_envs: formData.getAll('python'),
                repo_urls: getCustomRepos(formData, button),
                size: formData.get('size')
            })
        })
            .then(response => response.status === 200 ? instanceCreationSuccess(createInstanceButton) : instanceCreationFail(createInstanceButton))
            .catch(error => console.error('Error:', error));
    }
};


const deleteInstance = (instanceID) => {
    let url = BASE_URL + 'vms/' + instanceID;

    fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())  // Parses the JSON response
        .then(data => listInstances())
        .catch(error => console.error('Error:', error));
}

const repoValidationReset = () => {
    let button = document.getElementById('check');
    if (!button.classList.contains('btn-primary')) {
        button.classList.remove(...button.classList);
        button.classList.add('btn', 'btn-primary')
        button.innerText = 'Check Repository';
        button.disabled = false;
        button.removeAttribute('data-valid-repo');
        let createInstanceButton = document.getElementById('launch');
        instanceCreationReset(createInstanceButton);
    }
};

const repoValidationSuccess = () => {
    let button = document.getElementById('check');
    button.classList.replace('btn-primary', 'btn-outline-success');
    button.innerText = 'Valid Repository ✅';
    button.disabled = true;
    button.setAttribute('data-valid-repo', 'valid')
};

const repoValidationFail = () => {
    let button = document.getElementById('check');
    button.classList.replace('btn-primary', 'btn-outline-danger');
    button.innerText = 'Invalid Repository ❌';
    button.disabled = true;
    button.setAttribute('data-valid-repo', 'invalid')
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
    instanceCreationForm.addEventListener('show.bs.collapse', event => {
        instanceListTableCollapse.hide();
        let createInstanceButton = document.getElementById('launch');
        instanceCreationReset(createInstanceButton);
    });
}


document.getElementById('instanceListTable').addEventListener('shown.bs.collapse', listInstances);
document.getElementById('launch').addEventListener('click', createInstance);
document.getElementById('check').addEventListener('click', checkCustomRepo);
document.getElementById('customRepo').addEventListener('keyup', repoValidationReset);
document.getElementById('refresh').addEventListener('click', listInstances);
controlCollapse();
