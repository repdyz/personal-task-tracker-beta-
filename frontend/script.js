const API_URL = "/api";

const input = document.querySelector('input[type="text"]');
const addButton = document.querySelector('button');
const taskList = document.getElementById("task-list");
const allButton = document.getElementById("all-button");
const pendingButton = document.getElementById("pending-button");
const completedButton = document.getElementById("completed-button");

function renderTask(task) {
    const li = document.createElement("li");

    li.innerHTML = `
        <input type="checkbox" ${task.status === "completed" ? "checked" : ""}>
        ${task.title}
        <button class="delete-button">Delete</button>
    `;

    const checkbox = li.querySelector('input[type="checkbox"]');

    checkbox.addEventListener("change", async function () {
        const newStatus = checkbox.checked ? "completed" : "pending";

        await fetch(`${API_URL}/tasks/${task.id}?status=${newStatus}`, {
            method: "PATCH"
        });
    });

    const deleteButton = li.querySelector(".delete-button");

    deleteButton.addEventListener("click", async function () {
        await fetch(`${API_URL}/tasks/${task.id}`, {
            method: "DELETE"
        });

        li.remove();
    });

    taskList.appendChild(li);
}

addButton.addEventListener('click', async function () {
    const taskText = input.value.trim();

    if (taskText === "") {
        return;
    }

    const response = await fetch(`${API_URL}/tasks`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: taskText
        })
    });

    const task = await response.json();

    renderTask(task);

    input.value = "";
});

async function loadTasks(status = "") {
    let url = `${API_URL}/tasks`;

    if (status !== "") {
        url += `?status=${status}`;
    }

    const response = await fetch(url);

    const tasks = await response.json();

    taskList.innerHTML = "";

    tasks.forEach(function (task) {
        renderTask(task);
    });
}

allButton.addEventListener("click", function () {
    loadTasks();
});

pendingButton.addEventListener("click", function () {
    loadTasks("pending");
});

completedButton.addEventListener("click", function () {
    loadTasks("completed");
});

loadTasks();