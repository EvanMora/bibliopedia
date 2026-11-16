const palette = ["#667a61", "#a46e58", "#65758b", "#9a8358", "#765f7c", "#527c79", "#a35f59"];
const ratingLabels = ["", "No era para mí", "Estuvo bien", "Me gustó", "Me encantó", "Una historia inolvidable"];

const storedUserId = Number.parseInt(localStorage.getItem("bibliopedia-user-id") || "1", 10);
let userId = Number.isSafeInteger(storedUserId) && storedUserId > 0 ? storedUserId : 1;
let libraryEntries = [];
let currentFilter = "all";
let reviewRating = 0;
let searchRequest = 0;

const elements = {
  searchForm: document.querySelector("#search-form"),
  searchInput: document.querySelector("#search-input"),
  searchResults: document.querySelector("#search-results"),
  searchMessage: document.querySelector("#search-message"),
  libraryResults: document.querySelector("#library-results"),
  libraryMessage: document.querySelector("#library-message"),
  totalCount: document.querySelector("#total-count"),
  readCount: document.querySelector("#read-count"),
  libraryTotal: document.querySelector("#library-total"),
  profileUser: document.querySelector("#profile-user"),
  topbarUser: document.querySelector("#topbar-user"),
  reviewDialog: document.querySelector("#review-dialog"),
  reviewForm: document.querySelector("#review-form"),
  reviewBookId: document.querySelector("#review-book-id"),
  reviewBookTitle: document.querySelector("#review-book-title"),
  reviewDescription: document.querySelector("#review-description"),
  reviewError: document.querySelector("#review-error"),
  ratingHint: document.querySelector("#rating-hint"),
  settingsDialog: document.querySelector("#settings-dialog"),
  settingsForm: document.querySelector("#settings-form"),
  userIdInput: document.querySelector("#user-id-input"),
  settingsError: document.querySelector("#settings-error"),
  toastRegion: document.querySelector("#toast-region"),
};

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    throw new Error(body?.detail || `No se pudo completar la solicitud (${response.status}).`);
  }

  return body;
}

function showMessage(target, text, type = "") {
  target.textContent = text;
  target.className = `inline-message${type ? ` ${type}` : ""}`;
}

function clearMessage(target) {
  target.textContent = "";
  target.className = "inline-message";
}

function showToast(message, type = "") {
  const toast = document.createElement("div");
  toast.className = `toast${type ? ` ${type}` : ""}`;
  toast.textContent = message;
  elements.toastRegion.append(toast);
  window.setTimeout(() => toast.remove(), 3500);
}

function createCover(book, index) {
  const cover = document.createElement("div");
  cover.className = "book-cover";
  cover.style.setProperty("--cover", palette[index % palette.length]);

  const decoration = document.createElement("span");
  decoration.className = "cover-decoration";
  decoration.textContent = "✳";
  const title = document.createElement("span");
  title.className = "cover-title";
  title.textContent = book.book_title;
  const author = document.createElement("span");
  author.className = "cover-author";
  author.textContent = book.book_author;
  cover.append(decoration, title, author);
  return cover;
}

function createBookCard(book, { library = false, isRead = false } = {}) {
  const card = document.createElement("article");
  card.className = `book-card${library ? " library-card" : ""}`;
  card.append(createCover(book, Number(book.id_book) || 0));

  const info = document.createElement("div");
  info.className = "book-info";
  const title = document.createElement("h3");
  title.className = "book-title";
  title.textContent = book.book_title;
  const author = document.createElement("p");
  author.className = "book-author";
  author.textContent = book.book_author;
  const meta = document.createElement("div");
  meta.className = "book-meta";
  const year = document.createElement("span");
  year.textContent = book.year_of_publication || "Año desconocido";
  meta.append(year);
  if (book.publisher) {
    const dot = document.createElement("span");
    dot.className = "book-meta-dot";
    const publisher = document.createElement("span");
    publisher.textContent = book.publisher;
    meta.append(dot, publisher);
  }

  info.append(title, author, meta);

  if (library) {
    const actions = document.createElement("div");
    actions.className = "card-actions";
    const statusButton = document.createElement("button");
    statusButton.className = "card-action";
    statusButton.type = "button";
    statusButton.textContent = isRead ? "Marcar por leer" : "Marcar leído";
    statusButton.addEventListener("click", () => updateReadStatus(book.id_book, !isRead));
    actions.append(statusButton);

    if (isRead) {
      const reviewButton = document.createElement("button");
      reviewButton.className = "card-action secondary";
      reviewButton.type = "button";
      reviewButton.textContent = "Escribir reseña";
      reviewButton.addEventListener("click", () => openReviewDialog(book));
      actions.append(reviewButton);
    }

    info.append(actions);
  } else {
    const entry = libraryEntries.find((item) => item.id_book === book.id_book);
    const action = document.createElement("button");
    action.className = entry ? "read-badge" : "card-action";
    action.type = "button";
    action.textContent = entry ? (entry.is_read ? "Ya está en tus leídos" : "Ya está en tu biblioteca") : "Añadir a mi lista";
    action.disabled = Boolean(entry);
    if (!entry) action.addEventListener("click", () => addToLibrary(book.id_book, action));
    info.append(action);
  }

  card.append(info);
  return card;
}

function renderLibrary() {
  elements.libraryResults.replaceChildren();
  const filtered = libraryEntries.filter((entry) => {
    if (currentFilter === "read") return entry.is_read;
    if (currentFilter === "pending") return !entry.is_read;
    return true;
  });

  elements.libraryTotal.textContent = String(libraryEntries.length);
  elements.totalCount.textContent = String(libraryEntries.length);
  elements.readCount.textContent = String(libraryEntries.filter((entry) => entry.is_read).length);

  if (filtered.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    const content = document.createElement("div");
    const icon = document.createElement("span");
    icon.textContent = currentFilter === "read" ? "♡" : "✦";
    const heading = document.createElement("strong");
    heading.textContent = currentFilter === "read"
      ? "Aún no hay libros leídos"
      : currentFilter === "pending"
        ? "Tu lista por leer está vacía"
        : "Tu biblioteca empieza aquí";
    const description = document.createElement("p");
    description.textContent = "Explora el catálogo y guarda los libros que te gustaría leer.";
    content.append(icon, heading, description);
    empty.append(content);
    elements.libraryResults.append(empty);
    return;
  }

  filtered.forEach((entry) => {
    if (entry.book) {
      elements.libraryResults.append(createBookCard(entry.book, { library: true, isRead: entry.is_read }));
    }
  });
}

async function loadLibrary() {
  clearMessage(elements.libraryMessage);
  elements.libraryResults.setAttribute("aria-busy", "true");
  elements.profileUser.textContent = `Usuario ${userId}`;
  elements.topbarUser.textContent = `Usuario ${userId}`;

  try {
    const entries = await request(`/booklists/${encodeURIComponent(userId)}`);
    const hydratedEntries = await Promise.all(entries.map(async (entry) => {
      const book = await request(`/books/${encodeURIComponent(entry.id_book)}`);
      return { ...entry, book };
    }));
    libraryEntries = hydratedEntries;
    renderLibrary();
    return true;
  } catch (error) {
    libraryEntries = [];
    renderLibrary();
    showMessage(
      elements.libraryMessage,
      `${error.message} Comprueba el ID de usuario en la esquina superior.`,
      "error",
    );
    return false;
  } finally {
    elements.libraryResults.setAttribute("aria-busy", "false");
  }
}

async function searchBooks(keyword) {
  const requestId = ++searchRequest;
  elements.searchResults.replaceChildren();
  clearMessage(elements.searchMessage);

  if (keyword.length < 2) {
    showMessage(elements.searchMessage, "Escribe al menos dos caracteres para buscar en el catálogo.");
    return;
  }

  elements.searchResults.setAttribute("aria-busy", "true");
  try {
    const books = await request(`/books/search?keyword=${encodeURIComponent(keyword)}`);
    if (requestId !== searchRequest) return;
    if (books.length === 0) {
      showMessage(elements.searchMessage, "No encontramos libros con esa búsqueda. Prueba con otro título, autor o ISBN.");
      return;
    }
    books.forEach((book) => elements.searchResults.append(createBookCard(book)));
  } catch (error) {
    if (requestId === searchRequest) showMessage(elements.searchMessage, error.message, "error");
  } finally {
    if (requestId === searchRequest) elements.searchResults.setAttribute("aria-busy", "false");
  }
}

async function addToLibrary(bookId, button) {
  button.disabled = true;
  try {
    await request(`/booklists/${encodeURIComponent(userId)}/books/${encodeURIComponent(bookId)}/read-status?is_read=false`, {
      method: "PATCH",
    });
    await loadLibrary();
    await searchBooks(elements.searchInput.value.trim());
    showToast("Libro añadido a tu lista de lectura.");
  } catch (error) {
    button.disabled = false;
    showToast(error.message, "error");
  }
}

async function updateReadStatus(bookId, isRead) {
  try {
    await request(`/booklists/${encodeURIComponent(userId)}/books/${encodeURIComponent(bookId)}/read-status?is_read=${isRead}`, {
      method: "PATCH",
    });
    await loadLibrary();
    showToast(isRead ? "¡Un libro más terminado!" : "Libro movido a tu lista por leer.");
  } catch (error) {
    showToast(error.message, "error");
  }
}

function updateRating(value) {
  reviewRating = value;
  document.querySelectorAll(".rating-star").forEach((button) => {
    const selected = Number(button.dataset.rating) <= value;
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-checked", String(Number(button.dataset.rating) === value));
  });
  elements.ratingHint.textContent = ratingLabels[value];
}

function openReviewDialog(book) {
  reviewRating = 0;
  updateRating(0);
  elements.reviewError.textContent = "";
  elements.reviewForm.reset();
  elements.reviewBookId.value = String(book.id_book);
  elements.reviewBookTitle.textContent = book.book_title;
  elements.reviewDialog.showModal();
}

function openSettingsDialog() {
  elements.settingsError.textContent = "";
  elements.userIdInput.value = String(userId);
  elements.settingsDialog.showModal();
}

elements.searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  searchBooks(elements.searchInput.value.trim());
});

document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", () => {
    document.querySelectorAll(".nav-link").forEach((item) => item.classList.toggle("active", item === link));
  });
});

document.querySelectorAll(".filter-tab").forEach((button) => {
  button.addEventListener("click", () => {
    currentFilter = button.dataset.filter;
    document.querySelectorAll(".filter-tab").forEach((tab) => tab.classList.toggle("active", tab === button));
    renderLibrary();
  });
});

document.querySelectorAll(".rating-star").forEach((button) => {
  button.addEventListener("click", () => updateRating(Number(button.dataset.rating)));
  button.addEventListener("mouseenter", () => {
    document.querySelectorAll(".rating-star").forEach((star) => {
      star.classList.toggle("hovered", Number(star.dataset.rating) <= Number(button.dataset.rating));
    });
  });
  button.addEventListener("focus", () => {
    document.querySelectorAll(".rating-star").forEach((star) => {
      star.classList.toggle("hovered", Number(star.dataset.rating) <= Number(button.dataset.rating));
    });
  });
});

document.querySelector(".rating-stars").addEventListener("mouseleave", () => {
  document.querySelectorAll(".rating-star").forEach((star) => star.classList.remove("hovered"));
});

elements.reviewForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (reviewRating === 0) {
    elements.reviewError.textContent = "Elige una calificación antes de guardar.";
    return;
  }

  const submitButton = elements.reviewForm.querySelector('[type="submit"]');
  submitButton.disabled = true;
  elements.reviewError.textContent = "";
  try {
    await request("/reviews", {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        book_id: Number(elements.reviewBookId.value),
        qualifications: reviewRating,
        description: elements.reviewDescription.value.trim() || null,
      }),
    });
    elements.reviewDialog.close();
    showToast("Tu reseña quedó guardada.");
  } catch (error) {
    elements.reviewError.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

elements.settingsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const selectedId = Number(elements.userIdInput.value);
  if (!Number.isSafeInteger(selectedId) || selectedId < 1) {
    elements.settingsError.textContent = "Ingresa un ID de usuario válido.";
    return;
  }
  const previousId = userId;
  userId = selectedId;
  localStorage.setItem("bibliopedia-user-id", String(userId));
  elements.settingsDialog.close();
  const loaded = await loadLibrary();
  if (!loaded) {
    const failedId = userId;
    userId = previousId;
    localStorage.setItem("bibliopedia-user-id", String(userId));
    await loadLibrary();
    showToast(`No se pudo cargar el usuario ${failedId}. Revisa que exista en la base de datos.`, "error");
  }
});

document.querySelectorAll("#open-settings, #open-settings-mobile").forEach((button) => {
  button.addEventListener("click", openSettingsDialog);
});

document.querySelectorAll("[data-close-dialog]").forEach((button) => {
  button.addEventListener("click", () => button.closest("dialog").close());
});

document.querySelectorAll("dialog").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
});

loadLibrary();
