import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Navbar from "./components/Navbar";
import TextAnalysis from "./components/TextAnalysis";
import QRScan from "./components/QRScan";
import ResultCard from "./components/ResultCard";
import "./App.css";

const tagVariants = {
  hidden: { scale: 0.85, opacity: 0 },
  visible: (i) => ({
    scale: 1,
    opacity: 1,
    transition: { delay: i * 0.06, type: "spring", stiffness: 340, damping: 24 },
  }),
};

function App() {
  const [activeTab,   setActiveTab]   = useState("text");
  const [inputText,   setInputText]   = useState("");
  const [qrFile,      setQrFile]      = useState(null);
  const [prediction,  setPrediction]  = useState("");
  const [isScam,      setIsScam]      = useState(null);
  const [confidence,  setConfidence]  = useState(0);
  const [explanation, setExplanation] = useState([]);
  const [loading,     setLoading]     = useState(false);
  const [qrModalOpen, setQrModalOpen] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  const handleExplain = async () => {
  if (showExplanation) {
    setShowExplanation(false);
    return;
  }

  if (!inputText) return;

  setLoadingExplanation(true);
  setShowExplanation(true);

  try {
    const res = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: inputText, explain: true }),
    });

    const data = await res.json();
    setExplanation(data.explanation || []);
  } catch {
    setExplanation(["Failed to load explanation"]);
  } finally {
    setLoadingExplanation(false);
  }
};

  async function analyzeText(text) {
    if (!text) return;
    setLoading(true); setPrediction("Analyzing…");
    try {
      const res  = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text }),
      });
      const data = await res.json();
      setPrediction(data.prediction.toUpperCase());
      setIsScam(data.prediction === "scam" ? "scam" : data.prediction === "likely spam" ? "likely" : "legit");
      setConfidence(data.confidence * 100);
      setExplanation([]);
      setShowExplanation(false);
    } catch {
      setPrediction("Error"); setIsScam(null); setConfidence(0); setExplanation([]);
    } finally { setLoading(false); }
  }

  async function analyzeQr(file) {
    if (!file) return;
    setLoading(true); setPrediction("Analyzing…");
    setIsScam(null); setConfidence(0); setExplanation([]);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res  = await fetch("http://127.0.0.1:8000/predict-qr", { method: "POST", body: fd });
      const data = await res.json();
      if (data.prediction) {
        setPrediction(data.prediction.toUpperCase());
        setIsScam(data.prediction === "scam" ? "scam" : data.prediction === "likely scam" ? "likely" : "legit");
        setConfidence(data.confidence ? data.confidence * 100 : 0);
        setExplanation(data.explanation || []);
      } else if (data.url_risks?.length) {
        setPrediction(data.url_risks[0]); setIsScam(null); setConfidence(0); setExplanation([]);
      } else if (data.detail?.includes("No QR code found")) {
        setPrediction("No QR code found"); setIsScam(null); setConfidence(0); setExplanation([]);
      } else {
        setPrediction("No Result"); setIsScam(null); setConfidence(0); setExplanation([]);
      }
    } catch {
      setPrediction("Error"); setIsScam(null); setConfidence(0); setExplanation([]);
    } finally { setLoading(false); setQrModalOpen(false); setQrFile(null); }
  }

  useEffect(() => {
    setPrediction(""); setLoading(false);
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("qrImage")) {
      setActiveTab("qr");
      chrome.storage?.local.get(["qrImageUrl"], (res) => {
        if (res?.qrImageUrl) {
          setLoading(true); setPrediction("Analyzing…");
          fetch(res.qrImageUrl).then(r => r.blob()).then(blob => {
            analyzeQr(new File([blob], "qr-image.png", { type: blob.type }));
          }).catch(() => { setPrediction("Error loading image"); setLoading(false); });
        }
      });
    } else {
      chrome.storage?.local.get(["selectedText"], (res) => {
        if (res?.selectedText) { setInputText(res.selectedText); analyzeText(res.selectedText); }
      });
    }
  }, []);

  const shieldEmoji = isScam === "scam" ? "🚫" : isScam === "likely" ? "⚠️" : isScam === "legit" ? "✅" : "🛡️";
  const badgeClass  = isScam === "scam" ? "scam" : isScam === "likely" ? "likely" : isScam === "legit" ? "legit" : "neutral";
  const bgClass     = isScam === "scam" ? "scam-bg" : isScam === "likely" ? "likely-bg" : isScam === "legit" ? "safe-bg" : "";
  const cardClass   = isScam === "scam" ? "scam-detected" : isScam === "likely" ? "likely-detected" : isScam === "legit" ? "safe-detected" : "";

  const copyReport = () => {
    navigator.clipboard.writeText(
      `🛡️ ScamShield Report\nStatus: ${prediction}\nConfidence: ${confidence.toFixed(1)}%\nFlags: ${explanation.join(", ")}`
    );
  };

  return (
    <div className={`app-shell ${bgClass}`}>

      {/* ── Top bar: brand + navbar ── */}
      <div className="app-topbar">
        <div className="header">
          <div className="brand-group">
            <motion.div
              className="shield-icon"
              animate={loading ? { scale: [1, 1.12, 1] } : {}}
              transition={{ repeat: Infinity, duration: 1.4 }}
            >
              {shieldEmoji}
            </motion.div>
            <div className="brand-info">
              <span className="brand-name">ScamShield</span>
              <span className="brand-sub">AI-powered scam detection</span>
            </div>
          </div>

          <AnimatePresence mode="wait">
            <motion.span
              key={prediction}
              className={`badge ${badgeClass}`}
              initial={{ opacity: 0, x: 8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.18 }}
            >
              {prediction || "Ready"}
            </motion.span>
          </AnimatePresence>
        </div>

        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>

      {/* ── Scrollable content ── */}
      <div className="app-body">
        <div className={`card ${cardClass} ${activeTab === "qr" ? "card-compact" : ""}`}>

          {/* Input tab */}
          {activeTab === "text" ? (
            <TextAnalysis
              inputText={inputText}
              setInputText={setInputText}
              loading={loading}
              analyzeText={analyzeText}
            />
          ) : (
            <QRScan
              qrModalOpen={qrModalOpen}
              setQrModalOpen={setQrModalOpen}
              qrFile={qrFile}
              setQrFile={setQrFile}
              loading={loading}
              analyzeQr={analyzeQr}
            />
          )}

          <div className="divider" />

          {/* Result */}
        <ResultCard
          isScam={isScam}
          confidence={confidence}
          explanation={explanation}
          loading={loading}
          tagVariants={tagVariants}
          activeTab={activeTab}
          handleExplain={handleExplain}
          showExplanation={showExplanation}
          loadingExplanation={loadingExplanation}
        />
        </div>

        {/* Actions below the card */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <motion.button
            className="btn btn-primary"
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.985 }}
            onClick={() => window.close()}
          >
            Dismiss
          </motion.button>
          <motion.button
            className="btn btn-ghost"
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.985 }}
            onClick={copyReport}
          >
            Copy Security Report
          </motion.button>
        </div>
      </div>
    </div>
  );
}

export default App;