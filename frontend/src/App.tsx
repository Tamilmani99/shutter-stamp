import { useRef, useState } from "react";
import {
  ArrowDown,
  ArrowRight,
  Check,
  Heart,
  Mail,
  Sparkles,
  Star,
  Upload,
  X,
} from "lucide-react";

const styles = [
  {
    id: "lofi",
    number: "01 / THE IMPERFECT",
    name: "Lo-Fi",
    description:
      "Grainy textures, faded colours and a nostalgic film feeling.",
    image: "/styles/lofi.jpg",
  },
  {
    id: "postcard",
    number: "02 / THE CLASSIC",
    name: "Postcard",
    description:
      "A vintage postcard look for somewhere worth remembering.",
    image: "/styles/postcard.jpg",
  },
  {
    id: "with-love",
    number: "03 / THE PERSONAL",
    name: "Postcard With Letter",
    description:
      "A postcard with a personal letter and a little extra love.",
    image: "/styles/with-love.jpg",
  },
];

const steps = [
  {
    number: "01",
    title: "Pick a photograph",
    description:
      "Choose a JPG or JPEG image from your device. A favourite moment is a good place to start.",
    icon: <Upload size={24} />,
  },
  {
    number: "02",
    title: "Find your style",
    description:
      "Choose Lo-Fi, Postcard or Postcard With Letter. Each gives your photograph a different personality.",
    icon: <Sparkles size={24} />,
  },
  {
    number: "03",
    title: "Keep the memory",
    description:
      "Preview your selection and download it. Your memories deserve a place outside your camera roll.",
    icon: <Heart size={24} />,
  },
];

const processSteps = [
  "Got it",
  "Processing",
  "Layering",
  "Polishing",
  "Done",
];

export default function App() {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [resultUrl, setResultUrl] = useState("");
  const [selectedStyle, setSelectedStyle] = useState("");

  const [place, setPlace] = useState("");
  const [year, setYear] = useState("");
  const [message, setMessage] = useState("");

  const [error, setError] = useState("");

  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState("");
  const [feedbackSent, setFeedbackSent] = useState(false);

  const [resultOpen, setResultOpen] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);

  const flowers = [
    {
      symbol: "✿",
      left: "5%",
      delay: "0s",
      duration: "13s",
      size: "13px",
    },
    {
      symbol: "✽",
      left: "13%",
      delay: "4s",
      duration: "16s",
      size: "10px",
    },
    {
      symbol: "✿",
      left: "22%",
      delay: "8s",
      duration: "14s",
      size: "12px",
    },
    {
      symbol: "✽",
      left: "31%",
      delay: "2s",
      duration: "17s",
      size: "9px",
    },
    {
      symbol: "✿",
      left: "43%",
      delay: "6s",
      duration: "15s",
      size: "14px",
    },
    {
      symbol: "✽",
      left: "54%",
      delay: "1s",
      duration: "18s",
      size: "10px",
    },
    {
      symbol: "✿",
      left: "64%",
      delay: "7s",
      duration: "14s",
      size: "12px",
    },
    {
      symbol: "✽",
      left: "73%",
      delay: "3s",
      duration: "16s",
      size: "9px",
    },
    {
      symbol: "✿",
      left: "84%",
      delay: "9s",
      duration: "15s",
      size: "13px",
    },
    {
      symbol: "✽",
      left: "93%",
      delay: "5s",
      duration: "17s",
      size: "10px",
    },
  ];

  function handleImageUpload(file?: File) {
    if (!file) return;

    setError("");

    if (!["image/jpeg", "image/jpg"].includes(file.type)) {
      setError("Please choose a JPG or JPEG image.");
      return;
    }

if (file.size > 20 * 1024 * 1024) {
  setError("Your image must be 20 MB or smaller.");
  return;
}

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    if (resultUrl) {
      URL.revokeObjectURL(resultUrl);
    }

    setSelectedImage(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResultUrl("");
    setResultOpen(false);

    setPlace("");
    setYear("");
    setMessage("");
  }

  function removeImage() {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    if (resultUrl) {
      URL.revokeObjectURL(resultUrl);
    }

    setSelectedImage(null);
    setPreviewUrl("");
    setResultUrl("");
    setError("");

    setPlace("");
    setYear("");
    setMessage("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  async function createPreview() {
    if (!selectedImage) {
      setError("Please upload a photograph first.");
      return;
    }

    if (!selectedStyle) {
      setError("Please choose one of the three styles.");
      return;
    }

    /*
     * POSTCARD
     * requires place + year
     */
    if (
      selectedStyle === "postcard" &&
      (!place.trim() || !year.trim())
    ) {
      setError("Please enter the place and year for your postcard.");
      return;
    }

    /*
     * POSTCARD WITH LETTER
     * requires place + year + message
     */
    if (
      selectedStyle === "with-love" &&
      (!place.trim() ||
        !year.trim() ||
        !message.trim())
    ) {
      setError(
        "Please enter the place, year and message for your postcard."
      );
      return;
    }

    setError("");
    setProcessing(true);
    setProcessingStep(0);

    let step = 0;

    function advance() {
      step += 1;

      if (step < processSteps.length - 1) {
        setProcessingStep(step);
      }
    }

    const progressTimer = window.setInterval(() => {
      if (step < processSteps.length - 2) {
        advance();
      }
    }, 700);

    const formData = new FormData();

    formData.append("file", selectedImage);
    formData.append("style", selectedStyle);
    formData.append("place", place.trim());
    formData.append("year", year.trim());
    formData.append("message", message.trim());

    try {
      const response = await fetch(
  `${import.meta.env.DEV ? "http://127.0.0.1:8000" : ""}/api/process`,
  {
    method: "POST",
    body: formData,
  }
);

      if (!response.ok) {
        throw new Error("Image processing failed.");
      }

      const resultBlob = await response.blob();

      const newResultUrl =
        URL.createObjectURL(resultBlob);

      if (resultUrl) {
        URL.revokeObjectURL(resultUrl);
      }

      setResultUrl(newResultUrl);
      setProcessingStep(processSteps.length - 1);

      window.setTimeout(() => {
        setProcessing(false);
        setResultOpen(true);
      }, 500);
    } catch (error) {
      console.error(error);

      setError(
        "Something went wrong while processing your image. Please try again."
      );

      setProcessing(false);
      setProcessingStep(0);
    } finally {
      window.clearInterval(progressTimer);
    }
  }

  function submitFeedback() {
    if (!rating || !feedback.trim()) {
      return;
    }

    setFeedbackSent(true);
  }

  function selectStyle(styleId: string) {
    setSelectedStyle(styleId);

    /*
     * Clear old style-specific information
     * when the user changes style.
     */
    setPlace("");
    setYear("");
    setMessage("");
    setError("");
  }

  return (
    <div className="site-shell">

      {/* NAVIGATION */}
      <header className="navbar">
        <nav className="container nav-inner">

          <a href="#home" className="brand">
            <img
              src="/shutter-stamp-camera.png"
              alt="Shutter Stamp camera"
              className="brand-logo"
              onError={(event) => {
                event.currentTarget.style.display = "none";
              }}
            />

            <span className="brand-name">
              shutter stamp<span>.</span>
            </span>
          </a>

          <div className="nav-links">
            <a href="#try-it">Try It</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#styles">Styles</a>
            <a href="#history">History</a>
            <a href="#feedback">Feedback</a>
          </div>

          <a href="#try-it" className="primary-button">
            Make a memory <ArrowRight size={15} />
          </a>

        </nav>
      </header>

      <main>

        {/* FALLING FLOWERS */}
        <div
          className="falling-flowers"
          aria-hidden="true"
        >
          {flowers.map((flower, index) => (
            <span
              key={index}
              className="falling-flower"
              style={{
                left: flower.left,
                animationDelay: flower.delay,
                animationDuration: flower.duration,
                fontSize: flower.size,
              }}
            >
              {flower.symbol}
            </span>
          ))}
        </div>

        {/* HERO */}
        <section
          id="home"
          className="container hero"
        >
          <div className="hero-copy">

            <div className="hero-kicker">
              <Sparkles size={14} />
              A little nostalgia, made by you
            </div>

            <h1 className="hero-title">
              Turn photographs into <em>memories.</em>
            </h1>

            <p className="hero-description">
              Some moments deserve more than a place in your camera roll.
              Give your photographs a timeless look and make something worth
              keeping.
            </p>

            <div className="hero-actions">
              <a
                href="#try-it"
                className="primary-button"
              >
                Create your memory
                <ArrowRight size={16} />
              </a>

              <a
                href="#how-it-works"
                className="text-link"
              >
                Discover how
                <ArrowDown size={15} />
              </a>
            </div>

            <div className="hero-note">
              <span className="hero-note-icon">
                <Heart size={16} />
              </span>

              Made for the moments that matter.
            </div>

          </div>

          {/* HERO ART */}
          <div className="hero-art">
            <div className="hero-paper">

              <div className="hero-paper-art">
                <img
                  src="/hero-memory.jpg"
                  alt="A memory captured by Shutter Stamp"
                />
              </div>

              <div className="hero-stamp">
                MEMORIES
              </div>

              <div className="hero-paper-caption">
                Wish you were here.
              </div>

            </div>

            <div className="hero-floating-note">
              Keep this moment.
            </div>
          </div>

        </section>

        {/* INTRO STRIP */}
        <section className="intro-strip">
          <div className="container intro-inner">
            <span>Less scrolling</span>
            <span>✳</span>
            <span>More remembering</span>
            <span>✳</span>
            <span>Made to be kept</span>
          </div>
        </section>

        {/* PHOTO EDITOR */}
        <section
          id="try-it"
          className="create-section"
        >
          <div className="container">

            <div className="center-heading">
              <p className="eyebrow">
                Your turn
              </p>

              <h2 className="section-heading">
                Let's make something memorable.
              </h2>

              <p className="section-description">
                Choose a photograph, pick a style and let the magic begin.
              </p>
            </div>

            <div className="create-grid">

              {/* UPLOAD */}
              <div className="editor-panel">

                <div className="panel-heading">
                  <p className="panel-step">
                    Step 01
                  </p>

                  <h3 className="panel-title">
                    Your photograph
                  </h3>

                  <p className="panel-subtitle">
                    Upload one JPG or JPEG image, up to 20 MB.
                  </p>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  hidden
                  onChange={(event) =>
                    handleImageUpload(
                      event.target.files?.[0]
                    )
                  }
                />

                {previewUrl ? (
                  <>
                    <div className="preview-frame">

                      <img
                        src={previewUrl}
                        alt="Uploaded photograph"
                      />

                      <button
                        type="button"
                        className="remove-image"
                        onClick={removeImage}
                        aria-label="Remove photograph"
                      >
                        <X size={17} />
                      </button>

                      <span className="file-name">
                        {selectedImage?.name}
                      </span>

                    </div>

                    <button
                      type="button"
                      className="change-photo"
                      onClick={() =>
                        fileInputRef.current?.click()
                      }
                    >
                      Choose another photograph
                    </button>
                  </>
                ) : (
                  <button
                    type="button"
                    className="upload-box"
                    onClick={() =>
                      fileInputRef.current?.click()
                    }
                  >
                    <span className="upload-icon">
                      <Upload size={25} />
                    </span>

                    <span className="upload-title">
                      Drop your photo here
                    </span>

                    <span className="upload-hint">
                      or click to browse your files
                    </span>

                    <span className="upload-limit">
                      JPG / JPEG · MAXIMUM 20 MB
                    </span>
                  </button>
                )}

              </div>

              {/* STYLE SELECTION */}
              <div className="editor-panel">

                <div className="panel-heading">
                  <p className="panel-step">
                    Step 02
                  </p>

                  <h3 className="panel-title">
                    Choose your style
                  </h3>

                  <p className="panel-subtitle">
                    Three ways to give your photograph a new feeling.
                  </p>
                </div>

                <div className="style-options">

                  {styles.map((style) => {

                    const isSelected =
                      selectedStyle === style.id;

                    return (
                      <button
                        key={style.id}
                        type="button"
                        className={`style-option ${
                          isSelected
                            ? "selected"
                            : ""
                        }`}
                        onClick={() =>
                          selectStyle(style.id)
                        }
                      >

                        <span className="style-option-copy">

                          <span className="style-option-number">
                            {style.number}
                          </span>

                          <span className="style-option-name">
                            {style.name}
                          </span>

                          <span className="style-option-description">
                            {style.description}
                          </span>

                        </span>

                        <span className="style-check">
                          <Check size={14} />
                        </span>

                      </button>
                    );
                  })}

                </div>
              </div>

            </div>

            {/* STYLE-SPECIFIC MEMORY INPUTS */}
            {selectedStyle && (
              <div className="memory-details">

                <div className="memory-details-heading">

                  <p className="eyebrow">
                    {selectedStyle === "lofi"
                      ? "ADD A LITTLE MEMORY"
                      : selectedStyle === "postcard"
                        ? "ADD A POSTCARD DETAIL"
                        : "ADD A LITTLE LETTER"}
                  </p>

                  <p className="memory-details-note">
                    {selectedStyle === "lofi"
                      ? "Optional — add a short sentence to keep with the photograph."
                      : selectedStyle === "postcard"
                        ? "Tell us where and when this memory belongs."
                        : "Add the place, year and a short personal message."}
                  </p>

                </div>

                {/* PLACE + YEAR ONLY FOR POSTCARD STYLES */}
                {(selectedStyle === "postcard" ||
                  selectedStyle === "with-love") && (
                  <div className="memory-details-row">

                    <div className="memory-field">

                      <label htmlFor="place">
                        Place
                      </label>

                      <input
                        id="place"
                        type="text"
                        value={place}
                        onChange={(event) =>
                          setPlace(event.target.value.slice(0, 80))
                        }
                        placeholder="e.g. Paris"
                        maxLength={80}
                      />

                    </div>

                    <div className="memory-field">

                      <label htmlFor="year">
                        Year
                      </label>

                      <input
                        id="year"
                        type="text"
                        inputMode="numeric"
                        value={year}
                        onChange={(event) =>
                          setYear(
                            event.target.value.replace(/\D/g, "").slice(0, 4)
                          )
                        }
                        placeholder="e.g. 1927"
                        maxLength={4}
                      />

                    </div>

                  </div>
                )}

                {/* MESSAGE FOR LO-FI AND POSTCARD WITH LETTER */}
                {(selectedStyle === "lofi" ||
                  selectedStyle === "with-love") && (
                  <div className="memory-field memory-message-field">

                    <label htmlFor="message">
                      {selectedStyle === "lofi"
                        ? "Optional sentence"
                        : "Message"}
                    </label>

<textarea
  id="message"
  value={message}
  onChange={(event) =>
    setMessage(event.target.value)
  }
  placeholder={
    selectedStyle === "lofi"
      ? "Write a short sentence to keep with this memory..."
      : "Write a short memory in English..."
  }
  maxLength={200}
  rows={3}
/>

<div className="character-count">
  {message.length} / 200
</div>

                  </div>
                )}

              </div>
            )}

            {/* ERROR */}
            {error && (
              <p
                className="form-error"
                role="alert"
              >
                {error}
              </p>
            )}

            {/* CREATE BUTTON */}
            <div className="create-action">

              <button
                type="button"
                className="primary-button"
                onClick={createPreview}
                disabled={processing}
              >
                {processing
                  ? "Preparing your preview..."
                  : "Create My Memory"}

                {!processing && (
                  <Sparkles size={16} />
                )}
              </button>

            </div>

            <p className="processing-note">
              Your photograph is sent to the Shutter Stamp processing backend
              and returned as your preview.
            </p>

          </div>
        </section>

        {/* PROCESSING OVERLAY */}
        {processing && (
          <div className="modal-backdrop">

            <div className="result-modal">

              <p className="eyebrow">
                A little patience
              </p>

              <h2 className="result-title">
                Preparing your preview
              </h2>

              <div className="feedback-form">

                {processSteps.map(
                  (step, index) => (
                    <p
                      key={step}
                      style={{
                        padding: "9px 0",
                        color:
                          index <= processingStep
                            ? "#986b49"
                            : "#aaa08f",
                        fontWeight:
                          index === processingStep
                            ? 700
                            : 400,
                      }}
                    >
                      {index < processingStep
                        ? "✓"
                        : "○"}{" "}
                      {step}
                    </p>
                  )
                )}

              </div>

            </div>

          </div>
        )}

        {/* RESULT PREVIEW */}
        {resultOpen && resultUrl && (
          <div className="modal-backdrop">

            <div className="result-modal">

              <button
                type="button"
                className="modal-close"
                onClick={() =>
                  setResultOpen(false)
                }
                aria-label="Close preview"
              >
                <X size={20} />
              </button>

              <p className="eyebrow">
                Your selection is ready
              </p>

              <h2 className="result-title">
                A memory worth keeping.
              </h2>

              <div className="result-paper">

                <img
                  src={resultUrl}
                  alt="Processed Shutter Stamp result"
                />

              </div>

              <p className="result-disclaimer">
                Your photograph has been processed by the Shutter Stamp
                backend.
              </p>

              <a
                className="download-link"
                href={resultUrl}
                download={`shutter-stamp-${
                  selectedStyle || "memory"
                }.jpg`}
              >
                Download your memory
                <ArrowRight size={16} />
              </a>

            </div>

          </div>
        )}

        {/* HOW IT WORKS */}
        <section
          id="how-it-works"
          className="how-section"
        >
          <div className="container">

            <div className="center-heading">

              <p className="eyebrow">
                Simple as that
              </p>

              <h2 className="section-heading">
                Three little steps.
              </h2>

              <p className="section-description">
                No complicated editing. Just a photograph and a feeling.
              </p>

            </div>

            <div className="steps-grid">

              {steps.map((step) => (
                <article
                  className="step-card"
                  key={step.number}
                >

                  <div className="step-top">

                    <span className="step-number">
                      {step.number}
                    </span>

                    <span className="step-icon">
                      {step.icon}
                    </span>

                  </div>

                  <h3>
                    {step.title}
                  </h3>

                  <p>
                    {step.description}
                  </p>

                </article>
              ))}

            </div>

          </div>
        </section>

        {/* STYLE GALLERY */}
        <section
          id="styles"
          className="gallery-section"
        >
          <div className="container">

            <div className="center-heading">

              <p className="eyebrow">
                Find your feeling
              </p>

              <h2 className="section-heading">
                Three styles. Three stories.
              </h2>

              <p className="section-description">
                Every photograph tells a story. Give yours a look that feels
                just right.
              </p>

            </div>

            <div className="gallery-grid">

              {styles.map((style, index) => (
                <button
                  type="button"
                  className="gallery-card"
                  key={style.id}
                  onClick={() => {
                    selectStyle(style.id);

                    document
                      .getElementById("try-it")
                      ?.scrollIntoView({
                        behavior: "smooth",
                      });
                  }}
                >

                  <div className="gallery-image-wrap">

                    <img
                      className="gallery-image"
                      src={style.image}
                      alt={`${style.name} style example`}
                    />

                  </div>

                  <div className="gallery-meta">

                    <div>

                      <span className="gallery-number">
                        0{index + 1} / STYLE
                      </span>

                      <h3 className="gallery-name">
                        {style.name}
                      </h3>

                    </div>

                    <span className="gallery-arrow">
                      <ArrowRight size={17} />
                    </span>

                  </div>

                  <p className="gallery-description">
                    {style.description}
                  </p>

                </button>
              ))}

            </div>

          </div>
        </section>

        {/* HISTORY */}
        <section
          id="history"
          className="history-section"
        >
          <div className="container">

            <div className="section-heading">

              <p className="eyebrow">
                A LITTLE HISTORY
              </p>

              <h2>
                Before every memory had a camera roll.
              </h2>

              <p className="section-intro">
                Long before photographs lived on phones and postcards
                travelled across the world, people were already finding ways
                to preserve moments and send them through time.
              </p>

            </div>

            <div className="history-grid">

              <article className="history-card">

                <div className="history-image-wrap">

                  <img
                    src="/history/oldest-photo.jpg"
                    alt="View from the Window at Le Gras"
                    className="history-image"
                  />

                </div>

                <div className="history-content">

                  <p className="history-label">
                    1826 / 1827
                  </p>

                  <h3>
                    View from the Window at Le Gras
                  </h3>

                  <p className="history-text">
                    The world's oldest surviving photograph is titled
                    <em>
                      View from the Window at Le Gras
                    </em>
                    , taken by French inventor Joseph Nicéphore Niépce around
                    1826 or 1827.
                  </p>

                  <p className="history-text">
                    Niépce created the image using heliography on a pewter
                    plate coated with bitumen. The exposure required at least
                    eight hours, capturing the rooftops and landscape from
                    his estate in Burgundy, France.
                  </p>

                </div>

              </article>

              <article className="history-card">

                <div className="history-image-wrap">

                  <img
                    src="/history/oldest-postcard.jpg"
                    alt="The Penny Penates postcard"
                    className="history-image"
                  />

                </div>

                <div className="history-content">

                  <p className="history-label">
                    14 JULY 1840
                  </p>

                  <h3>
                    The Penny Penates
                  </h3>

                  <p className="history-text">
                    The world's oldest surviving postcard is the
                    <em>
                      Penny Penates
                    </em>
                    , a hand-drawn caricature mailed in the United Kingdom on
                    14 July 1840.
                  </p>

                  <p className="history-text">
                    Created by Theodore Hook, the card depicts postal officers
                    gathered around an inkwell. It is especially significant
                    because it bears the only known Penny Black stamp on a
                    postcard.
                  </p>

                </div>

              </article>

            </div>

          </div>
        </section>

        {/* FEEDBACK */}
        <section
          id="feedback"
          className="feedback-section"
        >
          <div className="container feedback-grid">

            <div className="feedback-copy">

              <p className="eyebrow">
                A little note
              </p>

              <h2 className="section-heading">
                Tell us what you think.
              </h2>

              <p>
                Shutter Stamp is made with care. Your feedback helps us make
                it even better. We would love to hear from you.
              </p>

              <p>

                <Heart
                  size={17}
                  style={{
                    display: "inline",
                    verticalAlign: "middle",
                    color: "#986b49",
                    marginRight: 8,
                  }}
                />

                Made by Tamilmani.

              </p>

            </div>

            <div className="feedback-form">

              {feedbackSent ? (
                <div className="feedback-success">

                  <span className="feedback-success-icon">
                    <Check size={25} />
                  </span>

                  <h3>
                    Thank you!
                  </h3>

                  <p>
                    Your feedback has been recorded in this preview.
                  </p>

                </div>
              ) : (
                <>
                  <h3>
                    Leave a little feedback
                  </h3>

                  <p>
                    How was your experience?
                  </p>

                  <div className="rating-row">

                    {[1, 2, 3, 4, 5].map(
                      (value) => (
                        <button
                          key={value}
                          type="button"
                          className={`rating-star ${
                            value <= rating
                              ? "active"
                              : ""
                          }`}
                          onClick={() =>
                            setRating(value)
                          }
                          aria-label={`Rate ${value} out of 5`}
                        >
                          <Star
                            size={26}
                            fill={
                              value <= rating
                                ? "currentColor"
                                : "none"
                            }
                          />
                        </button>
                      )
                    )}

                  </div>

                  <label
                    className="feedback-label"
                    htmlFor="feedback-message"
                  >
                    Your message
                  </label>

                  <textarea
                    id="feedback-message"
                    className="feedback-textarea"
                    value={feedback}
                    onChange={(event) =>
                      setFeedback(event.target.value)
                    }
                    placeholder="Share your thoughts..."
                  />

                  <button
                    type="button"
                    className="primary-button feedback-submit"
                    onClick={submitFeedback}
                    disabled={
                      !rating ||
                      !feedback.trim()
                    }
                  >
                    Send feedback
                    <Mail size={16} />
                  </button>
                </>
              )}

            </div>

          </div>
        </section>

      </main>

      {/* FOOTER */}
      <footer className="footer">
        <div className="container">

          <div className="footer-top">

            <div>

              <a
                href="#home"
                className="brand"
              >
                <span className="brand-name">
                  shutter stamp<span>.</span>
                </span>
              </a>

              <p className="footer-tagline">
                Turn photographs into memories.
              </p>

            </div>

            <div className="footer-links">

              <a href="#try-it">
                Try It
              </a>

              <a href="#how-it-works">
                How It Works
              </a>

              <a href="#styles">
                Styles
              </a>

              <a href="#feedback">
                Feedback
              </a>

            </div>

          </div>

          <div className="footer-bottom">
            © 2026 Shutter Stamp. Made to keep the moments that matter.
          </div>

        </div>
      </footer>

    </div>
  );
}