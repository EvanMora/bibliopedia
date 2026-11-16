const palette = ["#667a61", "#a46e58", "#65758b", "#9a8358", "#765f7c", "#527c79", "#a35f59"];
const ratingLabels = ["", "No era para mí", "Estuvo bien", "Me gustó", "Me encantó", "Una historia inolvidable"];

let currentUser = null;
let libraryEntries = [];
let currentFilter = "all";
let reviewRating = 0;
let searchRequest = 0;
let authMode = "login";

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
  profileName: document.querySelector("#profile-name"),
  profileUser: document.querySelector("#profile-user"),
  topbarUser: document.querySelector("#topbar-user"),
  adminPanel: document.querySelector("#admin-panel"),
  adminUsers: document.querySelector("#admin-users"),
  adminMessage: document.querySelector("#admin-message"),
  reviewDialog: document.querySelector("#review-dialog"),
  reviewForm: document.querySelector("#review-form"),
  reviewBookId: document.querySelector("#review-book-id"),
  reviewBookTitle: document.querySelector("#review-book-title"),
  reviewDescription: document.querySelector("#review-description"),
  reviewError: document.querySelector("#review-error"),
  reviewSubmit: document.querySelector("#review-form [type=submit]"),
  ratingHint: document.querySelector("#rating-hint"),
  authDialog: document.querySelector("#auth-dialog"),
  authForm: document.querySelector("#auth-form"),
  authName: document.querySelector("#auth-name"),
  authEmail: document.querySelector("#auth-email"),
  authPassword: document.querySelector("#auth-password"),
  authError: document.querySelector("#auth-error"),
  authHeading: document.querySelector("#auth-heading"),
  authSubmit: document.querySelector("#auth-submit"),
  accountDialog: document.querySelector("#account-dialog"),
  accountName: document.querySelector("#account-name"),
  accountDetails: document.querySelector("#account-details"),
  toastRegion: document.querySelector("#toast-region"),
};

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    credentials: "same-origin",
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const error = new Error(body?.detail || `No se pudo completar la solicitud (${response.status}).`);
    error.status = response.status;
    throw error;
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

    const removeButton = document.createElement("button");
    removeButton.className = "card-action secondary";
    removeButton.type = "button";
    removeButton.textContent = "Quitar de mi biblioteca";
    removeButton.addEventListener("click", () => removeFromLibrary(book.id_book));
    actions.append(removeButton);

    if (isRead) {
      const reviewButton = document.createElement("button");
      reviewButton.className = "card-action secondary";
      reviewButton.type = "button";
      reviewButton.textContent = entryReviewLabel(book.id_book);
      reviewButton.addEventListener("click", () => openReviewDialog(book, findReview(book.id_book)));
      actions.append(reviewButton);
    }

    info.append(actions);
    const review = isRead ? findReview(book.id_book) : null;
    if (review) {
      const savedReview = document.createElement("div");
      savedReview.className = "saved-review";
      const savedRating = document.createElement("span");
      savedRating.className = "saved-review-rating";
      savedRating.textContent = `${"★".repeat(review.qualifications)}${"☆".repeat(5 - review.qualifications)}`;
      const savedDescription = document.createElement("p");
      savedDescription.textContent = review.description || "Sin comentario escrito.";
      const deleteReviewButton = document.createElement("button");
      deleteReviewButton.className = "card-action secondary";
      deleteReviewButton.type = "button";
      deleteReviewButton.textContent = "Eliminar reseña";
      deleteReviewButton.addEventListener("click", () => removeReview(book.id_book));
      savedReview.append(savedRating, savedDescription, deleteReviewButton);
      info.append(savedReview);
    }
  } else {
    const entry = libraryEntries.find((item) => item.id_book === book.id_book);
    const action = document.createElement("button");
    action.className = entry ? "read-badge" : "card-action";
    action.type = "button";
    action.textContent = entry
      ? (entry.is_read ? "Ya está en tus leídos" : "Ya está en tu biblioteca")
      : currentUser ? "Añadir a mi lista" : "Inicia sesión para guardar";
    action.disabled = Boolean(entry);
    if (!entry) action.addEventListener("click", () => {
      if (currentUser) addToLibrary(book.id_book, action);
      else openAuthDialog("login");
    });
    info.append(action);
  }

  card.append(info);
  return card;
}

function findReview(bookId) {
  return libraryEntries.find((entry) => entry.id_book === bookId)?.review || null;
}

function entryReviewLabel(bookId) {
  return findReview(bookId) ? "Ver / editar reseña" : "Escribir reseña";
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
  if (!currentUser) {
    libraryEntries = [];
    renderLibrary();
    showMessage(elements.libraryMessage, "Inicia sesión para ver y gestionar tu biblioteca.");
    elements.libraryResults.setAttribute("aria-busy", "false");
    return false;
  }

  try {
    const [entries, reviews] = await Promise.all([
      request(`/booklists/${encodeURIComponent(currentUser.id_user)}`),
      request("/reviews/me"),
    ]);
    const reviewsByBook = new Map(reviews.map((review) => [review.id_book, review]));
    const hydratedEntries = await Promise.all(entries.map(async (entry) => {
      const book = await request(`/books/${encodeURIComponent(entry.id_book)}`);
      return { ...entry, book, review: reviewsByBook.get(entry.id_book) || null };
    }));
    libraryEntries = hydratedEntries;
    renderLibrary();
    return true;
  } catch (error) {
    libraryEntries = [];
    renderLibrary();
    if (error.status === 401) {
      currentUser = null;
      updateAccountControls();
      showMessage(elements.libraryMessage, "Tu sesión ya no es válida. Inicia sesión de nuevo.", "error");
    } else {
      showMessage(elements.libraryMessage, error.message, "error");
    }
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
    await request(`/booklists/${encodeURIComponent(currentUser.id_user)}/books/${encodeURIComponent(bookId)}/read-status?is_read=false`, {
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
    await request(`/booklists/${encodeURIComponent(currentUser.id_user)}/books/${encodeURIComponent(bookId)}/read-status?is_read=${isRead}`, {
      method: "PATCH",
    });
    await loadLibrary();
    showToast(isRead ? "¡Un libro más terminado!" : "Libro movido a tu lista por leer.");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function removeFromLibrary(bookId) {
  const entry = libraryEntries.find((item) => item.id_book === bookId);
  if (!entry) return;
  if (!window.confirm(`¿Quitar “${entry.book.book_title}” de tu biblioteca? La reseña guardada se conservará.`)) {
    return;
  }

  try {
    await request(`/booklists/${encodeURIComponent(currentUser.id_user)}/books/${encodeURIComponent(bookId)}`, {
      method: "DELETE",
    });
    await loadLibrary();
    if (elements.searchInput.value.trim()) await searchBooks(elements.searchInput.value.trim());
    showToast("Libro quitado de tu biblioteca.");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function removeReview(bookId) {
  const entry = libraryEntries.find((item) => item.id_book === bookId);
  if (!entry?.review) return;
  if (!window.confirm(`¿Eliminar tu reseña de “${entry.book.book_title}”?`)) return;

  try {
    await request(`/reviews/${encodeURIComponent(bookId)}`, { method: "DELETE" });
    await loadLibrary();
    showToast("Reseña eliminada.");
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

function openReviewDialog(book, review = null) {
  elements.reviewForm.reset();
  updateRating(review?.qualifications || 0);
  elements.reviewError.textContent = "";
  elements.reviewBookId.value = String(book.id_book);
  elements.reviewBookTitle.textContent = book.book_title;
  elements.reviewDescription.value = review?.description || "";
  elements.reviewSubmit.textContent = review ? "Actualizar reseña" : "Guardar reseña";
  elements.reviewDialog.showModal();
}

function openAuthDialog(mode = "login") {
  authMode = mode;
  elements.authError.textContent = "";
  elements.authForm.reset();
  updateAuthMode();
  if (!elements.authDialog.open) elements.authDialog.showModal();
}

function updateAuthMode() {
  const registering = authMode === "register";
  elements.authHeading.textContent = registering ? "Crea tu cuenta" : "Inicia sesión";
  elements.authSubmit.textContent = registering ? "Crear cuenta" : "Iniciar sesión";
  elements.authName.hidden = !registering;
  elements.authName.previousElementSibling.hidden = !registering;
  elements.authName.required = registering;
  elements.authPassword.autocomplete = registering ? "new-password" : "current-password";
  elements.authPassword.minLength = registering ? 10 : 1;
  document.querySelectorAll("[data-auth-mode]").forEach((button) => {
    button.classList.toggle("active", button.dataset.authMode === authMode);
  });
}

function updateAccountControls() {
  const signedIn = Boolean(currentUser);
  const label = signedIn ? currentUser.email : "Ingresar";
  elements.profileName.textContent = signedIn ? currentUser.name : "Mi espacio";
  elements.profileUser.textContent = signedIn
    ? (currentUser.role === "admin" ? "Administrador" : "Lector")
    : "Invitado";
  elements.topbarUser.textContent = label;
  elements.adminPanel.hidden = !signedIn || currentUser.role !== "admin";
  if (signedIn && currentUser.role === "admin") loadAdminUsers();
}

async function loadCurrentUser() {
  try {
    const result = await request("/auth/me");
    currentUser = result.user;
  } catch (error) {
    if (error.status !== 401) showToast(error.message, "error");
    currentUser = null;
  }
  updateAccountControls();
  if (currentUser) {
    await loadLibrary();
  } else {
    await loadLibrary();
    openAuthDialog("login");
  }
}

async function loadAdminUsers() {
  clearMessage(elements.adminMessage);
  try {
    const users = await request("/admin/users");
    elements.adminUsers.replaceChildren();
    users.forEach((user) => {
      const row = document.createElement("tr");
      for (const value of [user.name, user.email]) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.append(cell);
      }
      const roleCell = document.createElement("td");
      roleCell.textContent = user.role === "admin" ? "Administrador" : "Lector";
      const actionCell = document.createElement("td");
      if (user.id_user === currentUser.id_user) {
        actionCell.textContent = "Tu cuenta";
      } else {
        const roleButton = document.createElement("button");
        roleButton.className = "card-action";
        roleButton.type = "button";
        roleButton.textContent = user.role === "admin" ? "Hacer lector" : "Hacer administrador";
        roleButton.addEventListener("click", () => updateRole(user.id_user, user.role === "admin" ? "reader" : "admin"));
        actionCell.append(roleButton);
      }
      row.append(roleCell, actionCell);
      elements.adminUsers.append(row);
    });
  } catch (error) {
    showMessage(elements.adminMessage, error.message, "error");
  }
}

async function updateRole(userId, role) {
  try {
    await request(`/admin/users/${encodeURIComponent(userId)}/role`, {
      method: "PATCH",
      body: JSON.stringify({ role }),
    });
    await loadAdminUsers();
    showToast("Permisos del usuario actualizados.");
  } catch (error) {
    showToast(error.message, "error");
  }
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
        book_id: Number(elements.reviewBookId.value),
        qualifications: reviewRating,
        description: elements.reviewDescription.value.trim() || null,
      }),
    });
    await loadLibrary();
    elements.reviewDialog.close();
    showToast("Tu reseña quedó guardada y ya aparece en tu biblioteca.");
  } catch (error) {
    elements.reviewError.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

elements.authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  elements.authError.textContent = "";
  elements.authSubmit.disabled = true;
  const registering = authMode === "register";
  try {
    const result = await request(registering ? "/auth/register" : "/auth/login", {
      method: "POST",
      body: JSON.stringify({
        ...(registering ? { name: elements.authName.value.trim() } : {}),
        email: elements.authEmail.value.trim(),
        password: elements.authPassword.value,
      }),
    });
    currentUser = result.user;
    updateAccountControls();
    await loadLibrary();
    if (elements.searchInput.value.trim()) await searchBooks(elements.searchInput.value.trim());
    elements.authDialog.close();
    showToast(registering ? "Cuenta creada. ¡Bienvenido a Bibliopedia!" : "Sesión iniciada.");
  } catch (error) {
    elements.authError.textContent = error.message;
  } finally {
    elements.authSubmit.disabled = false;
  }
});

async function logout() {
  try {
    await request("/auth/logout", { method: "POST" });
    currentUser = null;
    libraryEntries = [];
    updateAccountControls();
    renderLibrary();
    await loadLibrary();
    if (elements.searchInput.value.trim()) await searchBooks(elements.searchInput.value.trim());
    elements.accountDialog.close();
    showToast("Cerraste sesión correctamente.");
  } catch (error) {
    showToast(error.message, "error");
  }
}

function openAccountDialog() {
  if (!currentUser) {
    openAuthDialog("login");
    return;
  }
  elements.accountName.textContent = currentUser.name;
  elements.accountDetails.textContent = `${currentUser.email} · ${currentUser.role === "admin" ? "Administrador" : "Lector"}`;
  elements.accountDialog.showModal();
}

document.querySelectorAll("#open-settings, #open-settings-mobile").forEach((button) => {
  button.addEventListener("click", openAccountDialog);
});

document.querySelectorAll("[data-auth-mode]").forEach((button) => {
  button.addEventListener("click", () => {
    authMode = button.dataset.authMode;
    elements.authError.textContent = "";
    updateAuthMode();
  });
});

document.querySelector("#logout-button").addEventListener("click", logout);

document.querySelectorAll("[data-close-dialog]").forEach((button) => {
  button.addEventListener("click", () => button.closest("dialog").close());
});

document.querySelectorAll("dialog").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
});

loadCurrentUser();
