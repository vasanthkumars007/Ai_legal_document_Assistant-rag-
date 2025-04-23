const BASE_URL = "http://localhost:8000"; // adjust if using a different port

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/summary/`, {
    method: "POST",
    body: formData,
  });
  return response.json();
}

export async function askQuestion(query) {
  const formData = new FormData();
  formData.append("query", query);

  const response = await fetch(`${BASE_URL}/legal_chat/`, {
    method: "POST",
    body: formData,
  });
  return response.json();
}
