document.addEventListener("DOMContentLoaded", () => {
  // --- UPLOAD PAGE LOGIC ---
  const fileUpload = document.getElementById("file-upload");
  if (fileUpload) {
    const uploadBox = document.getElementById("upload-box");
    const progressSection = document.getElementById("progress-section");
    const fileNameDisplay = document.getElementById("file-name");

    const allowedExtensions = [
      ".pdf",
      ".docx",
      ".doc",
      ".txt",
      ".md",
      ".odt",
      ".rtf",
      ".html",
      ".epub",
    ];

    fileUpload.addEventListener("change", (event) => {
      const file = event.target.files[0];
      if (!file) return;

      const fileName = file.name;
      const fileExt = fileName
        .substring(fileName.lastIndexOf("."))
        .toLowerCase();

      if (!allowedExtensions.includes(fileExt)) {
        alert(
          "❌ Unsupported file type. Please upload a valid legal document."
        );
        fileUpload.value = ""; // reset input
        return;
      }

      fileNameDisplay.textContent = file.name;
      uploadBox.classList.add("hidden");
      progressSection.classList.remove("hidden");
      startProcessing(file); // ⬅ send file to backend
    });

    function startProcessing(file) {
      const formData = new FormData();
      formData.append("file", file);

      fetch("/upload", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          const taskId = data.task_id;
          console.log("Task ID:", taskId);

          pollPhase(taskId, "extract_text", 1, () => {
            pollPhase(taskId, "get_chunks", 2, () => {
              pollPhase(taskId, "get_faiss_index", 3, () => {
                const completeSection =
                  document.getElementById("complete-section");
                if (completeSection) completeSection.classList.remove("hidden");

                setTimeout(() => {
                  window.location.href = `/chat?task_id=${taskId}`;
                }, 1500);
              });
            });
          });
        })
        .catch((error) => {
          console.error("Error uploading file:", error);
        });
    }

    function pollPhase(taskId, phase, stepNumber, onComplete) {
      const phaseMap = {
        extract_text: "text_extraction",
        get_chunks: "chunk_creation",
        get_faiss_index: "embedding_generation",
      };

      const timeoutLimit = 900000; // 15 minutes
      const pollingInterval = 500;
      let elapsed = 0;

      const interval = setInterval(() => {
        fetch(`/progress/${taskId}/${phaseMap[phase]}`)
          .then((res) => res.json())
          .then((data) => {
            const percent = data.progress || 0;
            const labelKey = phaseMap[phase];
            updateProgressBar(labelKey, percent);

            if (percent === 100) {
              clearInterval(interval);
              onComplete();
            } else {
              elapsed += pollingInterval;
              if (elapsed >= timeoutLimit) {
                clearInterval(interval);
                showTimeoutError();
              }
            }
          })
          .catch((err) => {
            console.error(`Error polling ${phase} progress:`, err);
          });
      }, pollingInterval);
    }

    function showTimeoutError() {
      const errorBox = document.createElement("div");
      errorBox.className = "mt-4 text-red-400 text-center";
      errorBox.innerHTML = `
        <p class="font-semibold">⚠️ Oops! The process is taking longer than expected.</p>
        <p>Please try again later or consider re-uploading a smaller file.</p>
      `;
      const progressSection = document.getElementById("progress-section");
      if (progressSection) progressSection.appendChild(errorBox);
    }

    function updateProgressBar(step, percent) {
      const stepMap = {
        text_extraction: 1,
        chunk_creation: 2,
        embedding_generation: 3,
      };

      const stepNumber = stepMap[step];
      if (!stepNumber) return;

      const progressBar = document.getElementById(`progress-bar-${stepNumber}`);
      const progressText = document.getElementById(
        `progress-text-${stepNumber}`
      );
      const processLabel =
        progressBar.parentElement.previousElementSibling.children[0];

      if (progressBar && progressText) {
        progressBar.style.width = `${percent}%`;
        progressText.textContent = `${percent}%`;

        processLabel.classList.remove("text-gray-500");
        if (stepNumber === 1) processLabel.classList.add("text-purple-400");
        if (stepNumber === 2) processLabel.classList.add("text-teal-400");
        if (stepNumber === 3) processLabel.classList.add("text-pink-500");
      }
    }
  }

  // --- CHAT PAGE LOGIC ---
  let queryHistory = [];
  const chatForm = document.getElementById("chat-form");
  if (chatForm) {
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const userMessage = userInput.value.trim();
      if (userMessage === "") return;

      appendUserMessage(userMessage);
      const historyToSend = [...queryHistory];
      queryHistory.push(userMessage);
      if (queryHistory.length > 5) queryHistory.shift();
      userInput.value = "";

      setTimeout(() => {
        fetchAIResponse(userMessage, historyToSend);
      }, 1000);
    });

    function appendUserMessage(message) {
      const messageHTML = `
        <div class="flex items-start gap-3 justify-end">
          <div class="bg-gradient-to-br from-purple-600 to-pink-600 p-4 rounded-l-lg rounded-br-lg">
            <p class="text-white">${message}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
          </div>
        </div>
      `;
      chatBox.innerHTML += messageHTML;
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    function fetchAIResponse(userMessage, history) {
      const spinnerId = `spinner-${Date.now()}`;
      const spinnerHTML = `
        <div id="${spinnerId}" class="flex items-start gap-3 ai-message">
          <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-teal-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
          </div>
          <div class="bg-gray-800 p-4 rounded-r-lg rounded-bl-lg max-w-[80%] overflow-auto">
            <div class="text-white flex items-center gap-2">
              <div class="w-5 h-5 border-2 border-t-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Thinking...</span>
            </div>
          </div>
        </div>
      `;
      chatBox.innerHTML += spinnerHTML;
      chatBox.scrollTop = chatBox.scrollHeight;

      fetch(`/query/${taskId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userMessage, history }),
      })
        .then((response) => response.json())
        .then((data) => {
          const spinnerElement = document.getElementById(spinnerId);
          if (spinnerElement) {
            spinnerElement.outerHTML = generateAIMessageHTML(data.response);
            chatBox.scrollTop = chatBox.scrollHeight;
          }
        })
        .catch((error) => {
          console.error("Error fetching AI response:", error);
          const spinnerElement = document.getElementById(spinnerId);
          if (spinnerElement) {
            spinnerElement.outerHTML = generateAIMessageHTML(
              "**Sorry**, something went wrong."
            );
            chatBox.scrollTop = chatBox.scrollHeight;
          }
        });
    }

    function generateAIMessageHTML(message) {
      return `
        <div class="flex items-start gap-3 ai-message">
          <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-teal-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
          </div>
          <div class="bg-gray-800 p-4 rounded-r-lg rounded-bl-lg max-w-[80%] overflow-auto">
            <div class="text-white prose prose-invert">${marked.parse(
              message
            )}</div>
          </div>
        </div>
      `;
    }
  }
});
