import React from "react";
import { motion, AnimatePresence } from "framer-motion";

function ResultCard({
  isScam,
  confidence,
  explanation,
  loading,
  tagVariants,
  activeTab,
  handleExplain,
  showExplanation,
  loadingExplanation
}) {

  const fillClass =
    isScam === "scam"
      ? "scam"
      : isScam === "likely"
      ? "likely"
      : isScam === "legit"
      ? "legit"
      : "neutral";

  const isQR = activeTab === "qr";

  // Hide empty state
  if (!loading) {
    if (
      activeTab === "text" &&
      isScam === null &&
      confidence === 0 &&
      explanation.length === 0
    ) return null;

    if (activeTab === "qr" && isScam === null) return null;
  }

  // 🔥 Convert keywords → readable sentence
const explanationText =
  explanation.length > 0
    ? `This message was classified as ${
        isScam === "scam"
          ? "a scam"
          : isScam === "likely"
          ? "likely a scam"
          : "legitimate"
      } because it contains words like ${explanation.join(", ")}.`
    : "No strong suspicious patterns detected in the message.";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>

      {/* Confidence */}
      {!isQR && (
        <div className="confidence-section">
          <div className="label-row">
            <span className="label-text">Confidence Score</span>
            <motion.span
              className="percentage-text"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {loading ? "—" : `${confidence.toFixed(1)}%`}
            </motion.span>
          </div>

          <div className="progress-track">
            <motion.div
              className={`progress-fill ${fillClass}`}
              initial={{ width: 0 }}
              animate={{ width: loading ? "12%" : `${confidence}%` }}
              transition={{ duration: 1 }}
            />
          </div>
        </div>
      )}

      {/* 🔥 View Explanation Button */}
      {!isQR && !loading && isScam !== null && (
        <button className="btn btn-ghost" onClick={handleExplain}>
          {showExplanation ? "Hide Explanation" : "View Explanation"}
        </button>
      )}

      {/* 🔥 Explanation */}
      {!isQR && showExplanation && (
        <AnimatePresence>
          <motion.div
            className="explanation-section"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <span className="section-label">Explanation</span>

            {loadingExplanation ? (
              <p className="empty-text pulse">Generating explanation...</p>
            ) : (
              <>
                {/* Natural sentence */}
                <p style={{ fontSize: "14px", color: "#444", lineHeight: 1.6 }}>
                  {explanationText}
                </p>

                {/* Optional tags */}
                <div className="tags">
                  {explanation.map((reason, i) => (
                    <motion.span
                      key={reason}
                      custom={i}
                      variants={tagVariants}
                      initial="hidden"
                      animate="visible"
                      className="tag"
                    >
                      {reason}
                    </motion.span>
                  ))}
                </div>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      )}

      {/* QR */}
      {isQR && !loading && (
        <div className="empty-state">
          <p className="empty-text">
            Link scanned using Safe Browsing
          </p>
        </div>
      )}
    </div>
  );
}

export default ResultCard;