import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [source, setSource] = useState("");
  const [sourceType, setSourceType] = useState("topic");
  const [faqCount, setFaqCount] = useState(3);
  const [language, setLanguage] = useState("English");
  const [tone, setTone] = useState("Professional");

  const [faqs, setFaqs] = useState([]);
  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [regeneratingIndex, setRegeneratingIndex] = useState(null);

  const [error, setError] = useState("");

  // ==================================================
  // LOAD FAQ HISTORY
  // ==================================================

  const loadHistory = async () => {
    setHistoryLoading(true);

    try {
      const response = await fetch(`${API_URL}/history`);

      let data;

      try {
        data = await response.json();
      } catch {
        throw new Error(
          "Invalid response received from the server."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load FAQ history."
        );
      }

      setHistory(data.history || []);
    } catch (err) {
      console.error("History error:", err);

      if (err.name === "TypeError") {
        setError(
          "Unable to connect to the backend. Please make sure the API server is running."
        );
      } else {
        setError(
          err.message || "Unable to load FAQ history."
        );
      }
    } finally {
      setHistoryLoading(false);
    }
  };

  // ==================================================
  // LOAD HISTORY WHEN PAGE OPENS
  // ==================================================

  useEffect(() => {
    loadHistory();
  }, []);

  // ==================================================
  // GENERATE FAQs
  // ==================================================

  const generateFAQs = async () => {
    setError("");

    if (!source.trim()) {
      setError("Please enter a topic, text, or URL.");
      return;
    }

    const count = Number(faqCount);

    if (!Number.isInteger(count) || count < 1 || count > 10) {
      setError("FAQ count must be between 1 and 10.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/generate-faq`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          source_type: sourceType,
          source: source.trim(),
          faq_count: count,
          language: language,
          tone: tone,
        }),
      });

      let data;

      try {
        data = await response.json();
      } catch {
        throw new Error(
          "The server returned an invalid response."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to generate FAQs."
        );
      }

      if (!data.faqs || !Array.isArray(data.faqs)) {
        throw new Error(
          "The server returned an invalid FAQ response."
        );
      }

      setFaqs(data.faqs);

      await loadHistory();

    } catch (err) {
      console.error("Generate FAQ error:", err);

      if (err.name === "TypeError") {
        setError(
          "Unable to connect to the backend. Please make sure the API server is running."
        );
      } else {
        setError(
          err.message ||
            "Something went wrong while generating FAQs."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // ==================================================
  // REGENERATE FAQ
  // ==================================================

  const regenerateFAQ = async (index) => {
    setError("");
    setRegeneratingIndex(index);

    try {
      const response = await fetch(`${API_URL}/regenerate-faq`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          result: {
            faqs: faqs,
          },

          index: index,

          content: source,

          language: language,

          tone: tone,
        }),
      });

      let data;

      try {
        data = await response.json();
      } catch {
        throw new Error(
          "The server returned an invalid response."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to regenerate FAQ."
        );
      }

      if (!data.faqs || !Array.isArray(data.faqs)) {
        throw new Error(
          "The server returned an invalid FAQ response."
        );
      }

      setFaqs(data.faqs);

    } catch (err) {
      console.error("Regenerate FAQ error:", err);

      if (err.name === "TypeError") {
        setError(
          "Unable to connect to the backend. Please make sure the API server is running."
        );
      } else {
        setError(
          err.message ||
            "Something went wrong while regenerating the FAQ."
        );
      }
    } finally {
      setRegeneratingIndex(null);
    }
  };

  // ==================================================
  // DOWNLOAD TEXT FILE
  // ==================================================

  const downloadTXT = () => {
    if (faqs.length === 0) {
      setError("Generate FAQs before downloading.");
      return;
    }

    let content = "AI FAQ GENERATOR\n";
    content += "============================\n\n";

    content += `Source Type: ${sourceType}\n`;
    content += `Source: ${source}\n`;
    content += `Language: ${language}\n`;
    content += `Tone: ${tone}\n`;
    content += `Number of FAQs: ${faqs.length}\n\n`;

    content += "GENERATED FAQs\n";
    content += "============================\n\n";

    faqs.forEach((faq, index) => {
      content += `${index + 1}. ${faq.question}\n\n`;
      content += `${faq.answer}\n\n`;
      content += "----------------------------\n\n";
    });

    const blob = new Blob(
      [content],
      { type: "text/plain;charset=utf-8" }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "ai-faqs.txt";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  // ==================================================
  // DOWNLOAD JSON FILE
  // ==================================================

  const downloadJSON = () => {
    if (faqs.length === 0) {
      setError("Generate FAQs before downloading.");
      return;
    }

    const exportData = {
      source_type: sourceType,
      source: source,
      faq_count: faqs.length,
      language: language,
      tone: tone,
      faqs: faqs,
    };

    const content = JSON.stringify(
      exportData,
      null,
      2
    );

    const blob = new Blob(
      [content],
      { type: "application/json;charset=utf-8" }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "ai-faqs.json";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  // ==================================================
  // PRINT / SAVE AS PDF
  // ==================================================

  const printFAQs = () => {
    if (faqs.length === 0) {
      setError("Generate FAQs before exporting.");
      return;
    }

    window.print();
  };

  // ==================================================
  // RENDER
  // ==================================================

  return (
    <div className="app">

      {/* ==================================================
          HEADER
          ================================================== */}

      <h1>AI FAQ Generator</h1>

      <p className="subtitle">
        Generate professional FAQs from a topic, text, or URL.
      </p>

      {/* ==================================================
          GENERATOR FORM
          ================================================== */}

      <div className="form">

        <label>Source Type</label>

        <select
          value={sourceType}
          onChange={(e) => {
            setSourceType(e.target.value);
            setSource("");
            setError("");
          }}
          disabled={loading}
        >
          <option value="topic">Topic</option>
          <option value="text">Text</option>
          <option value="url">URL</option>
        </select>

        <label>Source</label>

        <textarea
          value={source}
          onChange={(e) => {
            setSource(e.target.value);
            setError("");
          }}
          placeholder={
            sourceType === "topic"
              ? "Example: Cloud Computing"
              : sourceType === "url"
              ? "https://example.com"
              : "Paste your content here..."
          }
          rows="6"
          disabled={loading}
        />

        <label>Number of FAQs</label>

        <input
          type="number"
          min="1"
          max="10"
          value={faqCount}
          onChange={(e) => {
            setFaqCount(e.target.value);
            setError("");
          }}
          disabled={loading}
        />

        <label>Language</label>

        <select
          value={language}
          onChange={(e) => {
            setLanguage(e.target.value);
            setError("");
          }}
          disabled={loading}
        >
          <option>English</option>
          <option>Hindi</option>
          <option>Nepali</option>
          <option>Bengali</option>
          <option>Urdu</option>
          <option>Tamil</option>
          <option>Telugu</option>
          <option>Marathi</option>
          <option>Gujarati</option>
          <option>Kannada</option>
          <option>Malayalam</option>
          <option>Punjabi</option>
          <option>Spanish</option>
          <option>French</option>
          <option>German</option>
          <option>Italian</option>
          <option>Portuguese</option>
        </select>

        <label>Tone</label>

        <select
          value={tone}
          onChange={(e) => {
            setTone(e.target.value);
            setError("");
          }}
          disabled={loading}
        >
          <option>Professional</option>
          <option>Friendly</option>
          <option>Simple</option>
        </select>

        <button
          onClick={generateFAQs}
          disabled={
            loading ||
            regeneratingIndex !== null
          }
        >
          {loading
            ? "Generating FAQs..."
            : "Generate FAQs"}
        </button>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

      </div>

      {/* ==================================================
          GENERATED FAQs
          ================================================== */}

      {faqs.length > 0 && (
        <div className="results">

          <h2>Generated FAQs</h2>

          {faqs.map((faq, index) => (

            <div
              className="faq-card"
              key={index}
            >

              <h3>
                {index + 1}. {faq.question}
              </h3>

              <p>
                {faq.answer}
              </p>

              <button
                className="regenerate-button"
                onClick={() =>
                  regenerateFAQ(index)
                }
                disabled={
                  loading ||
                  regeneratingIndex !== null
                }
              >
                {regeneratingIndex === index
                  ? "Regenerating..."
                  : "↻ Regenerate FAQ"}
              </button>

            </div>

          ))}

          {/* ==================================================
              EXPORT SECTION
              ================================================== */}

          <div className="export-section">

            <h2>Export FAQs</h2>

            <p className="export-description">
              Download your generated FAQs in your preferred format.
            </p>

            <div className="export-buttons">

              <button
                className="export-button"
                onClick={downloadTXT}
                disabled={
                  loading ||
                  regeneratingIndex !== null
                }
              >
                ↓ Download TXT
              </button>

              <button
                className="export-button"
                onClick={downloadJSON}
                disabled={
                  loading ||
                  regeneratingIndex !== null
                }
              >
                ↓ Download JSON
              </button>

              <button
                className="export-button"
                onClick={printFAQs}
                disabled={
                  loading ||
                  regeneratingIndex !== null
                }
              >
                🖨 Print / Save PDF
              </button>

            </div>

          </div>

        </div>
      )}

      {/* ==================================================
          FAQ HISTORY
          ================================================== */}

      <div className="history">

        <div className="history-header">

          <h2>FAQ History</h2>

          <button
            onClick={loadHistory}
            disabled={
              historyLoading ||
              loading ||
              regeneratingIndex !== null
            }
          >
            {historyLoading
              ? "Loading..."
              : "Refresh"}
          </button>

        </div>

        {history.length === 0 &&
          !historyLoading && (
            <p>
              No FAQ history available yet.
            </p>
          )}

        {historyLoading && (
          <p>
            Loading FAQ history...
          </p>
        )}

        {!historyLoading &&
          history.map((item) => (

            <div
              className="history-card"
              key={item.id}
            >

              <h3>
                {item.source_type.toUpperCase()}:{" "}
                {item.source}
              </h3>

              <p>
                <strong>FAQs:</strong>{" "}
                {item.faq_count}
              </p>

              <p>
                <strong>Language:</strong>{" "}
                {item.language}
              </p>

              <p>
                <strong>Tone:</strong>{" "}
                {item.tone}
              </p>

              <small>
                Created:{" "}
                {new Date(
                  item.created_at
                ).toLocaleString()}
              </small>

              <details>

                <summary>
                  View FAQs
                </summary>

                {item.faqs.map(
                  (faq, index) => (

                    <div
                      className="history-faq"
                      key={index}
                    >

                      <strong>
                        {index + 1}.{" "}
                        {faq.question}
                      </strong>

                      <p>
                        {faq.answer}
                      </p>

                    </div>

                  )
                )}

              </details>

            </div>

          ))}

      </div>

    </div>
  );
}

export default App;
