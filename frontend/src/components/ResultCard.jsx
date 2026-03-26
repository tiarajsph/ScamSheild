import React from "react";
import { motion, AnimatePresence } from "framer-motion";

function ResultCard({ isScam, confidence, explanation, loading, tagVariants }) {
  const fillClass = isScam === "scam" ? "scam" : isScam === "likely" ? "likely" : isScam === "legit" ? "legit" : "neutral";

  // Nothing to show yet
  if (!loading && isScam === null && confidence === 0 && explanation.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🔍</div>
        <p className="empty-text">Results will appear here after analysis</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {/* Confidence bar */}
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
            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          />
        </div>
      </div>

      {/* Key Indicators */}
      <AnimatePresence>
        {!loading && explanation.length > 0 && (
          <motion.div
            className="explanation-section"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <span className="section-label">Key Indicators</span>
            <div className="tags">
              {explanation.map((word, i) => (
                <motion.span
                  key={word}
                  custom={i}
                  variants={tagVariants}
                  initial="hidden"
                  animate="visible"
                  className="tag"
                >
                  {word}
                </motion.span>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default ResultCard;