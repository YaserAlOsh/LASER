// Importing necessary dependencies and components
import { useNavigate } from "react-router-dom";
import arrowLeft from "@iconify/icons-mdi/arrow-left";
import React, { useState, useRef, useEffect } from "react";
import { FaSearch } from "react-icons/fa";
import { motion, AnimatePresence } from "framer-motion";
import { Icon } from "@iconify/react";
import chevronDown from "@iconify/icons-mdi/chevron-down";
import { useSpring, animated } from "react-spring";
import Typewriter from "typewriter-effect";
import axiosJSON from "../axiosJSON";
import axiosFILES from "../axiosFILES";
import ReactPlayer from "react-player";
import { css } from '@emotion/react';
import { RingLoader } from 'react-spinners';

// Component for a loading page
const LoadingPage = () => {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Loading</h1>
        <Typewriter
          options={{
            strings: [
              "Loading Video",
              "Loading Summaries",
              "Loading Transcript",
            ],
            autoStart: true,
            loop: true,
          }}
        />
      </div>
    </div>
  );
};

// Component for a progress bar
const ProgressBar = ({ progress }) => {
  // Using react-spring for smooth animation
  const progressBarStyle = useSpring({
    width: `${progress}%`,
    from: { width: "0%" },
  });

  return (
    <div className="h-4 w-full bg-gray-200 rounded-full overflow-hidden">
      {/* Animated progress bar */}
      <animated.div
        className="h-full bg-blue-300 rounded-full"
        style={progressBarStyle}
      ></animated.div>
    </div>
  );
};

// Custom hook for toggling state
const useToggle = (initialState = false) => {
  const [state, setState] = React.useState(initialState);
  const toggle = React.useCallback(() => setState((state) => !state), []);
  return [state, toggle];
};

// Component for a search bar
const SearchBar = ({ onSearch }) => {
  const [searchText, setSearchText] = useState("");

  const handleSearch = () => {
    // Pass the searchText to the onSearch function
    onSearch(searchText);
  };

  return (
    <div className="border border-gray-300 rounded p-4 max-h-16 flex items-center">
      {/* Input for searching */}
      <input
        type="text"
        placeholder="Search..."
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        className="border border-gray-300 rounded p-2 mr-2"
      />
      {/* Button for triggering search */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className="bg-gray-700 text-white rounded p-2"
        onClick={handleSearch}
      >
        <FaSearch />
      </motion.button>
    </div>
  );
};

// Component for displaying video summaries
const Summary = ({ searchQuery, summaries, titles, segments, onSearch }) => {
  // Function to format time in seconds to minutes and seconds
  const formatTime = (timeInSeconds) => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  };
  const [activeTitle, setActiveTitle] = useState(null);

  // Handler for clicking on a title to toggle its display
  const handleTitleClick = (title) => {
    setActiveTitle(title === activeTitle ? null : title);
  };

  // Function to render highlighted text based on search query
  const renderHighlightedText = (text) => {
    if (!searchQuery || !text) return text;

    const regex = new RegExp(`(${searchQuery})`, 'gi');
    return text.split(regex).map((part, index) => {
      return regex.test(part) ? (
        <span key={index} className="bg-blue-100">
          {part}
        </span>
      ) : (
        part
      );
    });
  };

  return (
    <div className="bg-white p-4 max-h-16 ml-27 mr-27 ">
      <h2 className="text-xl font-semibold mb-2 text-gray-800">Summary Section</h2>
      <div className="flex bg-white border border-gray-300 p-4">
        {/* Titles Section */}
        {titles !== undefined && titles.length > 1 ? (
          <ul className="flex flex-col pr-4 border-r border-gray-300 h-[64rem] overflow-scroll">
            {titles.map((title, index) => (
              <li key={index} className="mb-2">
                {/* Button for each title */}
                <button
                  className={`hover:bg-gray-200 p-2 w-full ${
                    activeTitle === `title-${index}` ? 'bg-gray-700 text-white' : ''
                  } border border-white`}
                  onClick={() => handleTitleClick(`title-${index}`)}
                >
                  {renderHighlightedText(title)}
                  <br />
                  <span className="text-gray-500 ml-2">{formatTime(segments[index])}</span>
                </button>
              </li>
            ))}
          </ul>
        ) : null}

        {/* Summaries Section */}
        <div className="flex flex-col w-4/5">
          <ul className="divide-y divide-white">
            {summaries !== undefined && summaries.length > 0 ? (
              summaries.map((summary, index) => (
                <li
                  key={index}
                  id={`title-${index}`}
                  className={`mb-4 p-2 ${titles[index] == '' || activeTitle === `title-${index}` ? '' : 'hidden'}`}
                >
                  {/* Displaying title and summary */}
                  <h3 className="font-bold">{renderHighlightedText(titles[index])}</h3>
                  <p>{renderHighlightedText(summary)}</p>
                </li>
              ))
            ) : (
              <p>Generating Summaries...</p>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

// Function to format time in seconds to minutes and seconds
const formatTime = (timeInSeconds) => {
  const minutes = Math.floor(timeInSeconds / 60);
  const seconds = Math.floor(timeInSeconds % 60);
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
};

// Component for displaying the transcript
const Transcript = ({ transcriptData, transcriptRef, maxTranscriptHeight }) => {
  const [selected, setSelected] = useState(null);

  // Handler for clicking on a transcript entry
  const handleClick = (index, timestamp) => {
    setSelected(index);
  };

  // CSS override for the loading spinner
  const override = css`
    display: block;
    margin: 0 auto;
    border-color: red; // You can customize the color
  `;

  return (
    <div className="bg-gray p-4 h-full w-full overflow-y-auto mb-2" style={{ maxHeight: maxTranscriptHeight, overflowY: 'auto' }}>
      <h2 className="text-xl font-semibold mb-2 text-gray-800">Transcript</h2>

      {transcriptData ? (
        // Displaying the transcript entries
        <ul className="divide-y divide-gray-300">
          {transcriptData.map((entry, index) => (
            entry ? (
              <li key={index} className="py-1">
                {/* Clickable timestamp */}
                <a
                  href="#"
                  className={`text-gray-500 ${selected === index ? 'font-semibold' : ''}`}
                  onClick={() => handleClick(index, transcriptRef[index])}
                >
                  {formatTime(transcriptRef[index])}
                </a>
                {/* Displaying transcript text */}
                <p className="ml-2" style={{ color: '#a3b5c3', whiteSpace: 'pre-wrap' }}>
                  {entry}
                </p>
              </li>
            ) : null
          ))}
        </ul>
      ) : (
        // Displaying a loading spinner while fetching transcript
        <div className="flex items-center justify-center h-full">
          <RingLoader css={override} size={50} color={'#123abc'} loading={true} />
        </div>
      )}
    </div>
  );
};

// Component for playing YouTube videos
const VideoPlayerYoutube = ({ userInput }) => {
  return (
    <div className="relative pt-[56.25%] pb-12 ">
      {/* ReactPlayer component for YouTube videos */}
      <ReactPlayer
        className="absolute top-0 left-0 w-full h-full"
        controls={false}
        url={userInput}
        playing={true}
        allowfullscreen={true}
        config={{
          youtube: {
            playerVars: { modestbranding: 1, cc_load_policy: 0 }
          }
        }}
      />
    </div>
  );
};

// Component for playing local video files
const VideoPlayerFile = ({ videoFile }) => {
  return (
    <div className="relative bg-gray-200 p-4">
      {/* HTML5 video player for local video files */}
      <video width="1000" controls className="w-5/6 h-5/6 object-cover ml-14">
        <source src={videoFile} type="video/mp4" />
      </video>
    </div>
  );
};

// Component for a QA chat interface
const QAChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);

  const [chat, setChat] = useState([]);
  const [newQuestion, setNewQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  // Function to fetch an answer from the backend
  const fetchAnswerFromBackend = async (question) => {
    try {
      const response = await axiosJSON.post(`${global.config.path}/answer_question`, { question });
      const data = response.data;
      console.log(response);
      console.log(data);

      setAnswer(data.answer);
      return data.answer;
    } catch (error) {
      console.error("Error fetching answer:", error);
      return "Error fetching answer.";
    }
  };

  // Function to add a new question and fetch the answer
  const addQuestion = async () => {
    if (newQuestion.trim() !== "") {
      const updatedChat = [...chat, { text: newQuestion, isQuestion: true }];
      setChat(updatedChat);
      setNewQuestion("");

      try {
        // Fetch the answer and add it to the chat
        const answer = await fetchAnswerFromBackend(newQuestion);
        updatedChat.push({ text: answer, isQuestion: false });
        setChat(updatedChat);
      } catch (error) {
        // Handle the error and update the chat with an error message
        console.error("Error fetching answer:", error);
        updatedChat.push({ text: "Error fetching answer.", isQuestion: false });
        setChat(updatedChat);
      }
    }
  };

  // Effect to scroll to the bottom of the chat when it updates
  useEffect(() => {
    const chatContainer = document.getElementById("chat-container");
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }, [chat]);

  return (
    <div className="border border-gray-300 rounded p-4">
      <h2 className="text-xl font-semibold mb-2 text-gray-800">
        Ask a Question
      </h2>{" "}
      <div className="mb-4">
        <div className="mb-2">
          {/* Input for asking a question */}
          <input
            type="text"
            placeholder="Ask a question"
            className="w-full p-2 border border-gray-300 rounded"
            value={newQuestion}
            onChange={(e) => setNewQuestion(e.target.value)}
          />
        </div>
        {/* Button to submit the question */}
        <button
          onClick={addQuestion}
          className="bg-gray-700 text-white px-3 py-2 rounded"
        >
          Ask
        </button>
        <div
          id="chat-container"
          className="mt-4 p-2 border border-gray-300 rounded h-64 overflow-y-auto"
          style={{ backgroundColor: "#f0f0f0" }}
        >
          {/* Displaying the chat messages */}
          {chat.map((message, index) => (
            <div
              key={index}
              className={`p-2 rounded ${
                message.isQuestion ? "bg-blue-500 text-white" : "bg-gray-200"
              }`}
            >
              {message.text}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};


// WelcomeUsername component: Displays a welcome message with username, an option to show email, and logout functionality.
const WelcomeUsername = ({ username, email, onLogout }) => {
  const [showEmail, toggleEmail] = useToggle(); // Custom hook to toggle the display of the email section
  const [account, setAccount] = useState(null); // State to manage user account information
  
  const handleLogout = async () => {
    try {
      // Perform a logout action using axios
      await axiosJSON.post(`${global.config.path}/logout`);
      setAccount(null); // Clear user account information
      window.location.href = "/"; // Redirect to the home page
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  return (
    <div className="flex items-center relative">
      <span className="text-gray-600 mr-2">Welcome, {username}</span>
      <button
        className="flex items-center bg-gray-200 hover:bg-gray-300 text-gray-800 px-2 py-1 rounded"
        onClick={toggleEmail}
      >
        <Icon icon={chevronDown} className="h-4 w-4" />
      </button>
      <AnimatePresence>
        {showEmail && (
          // Animated email box that appears when showEmail is true
          <motion.div
            key="email-box"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute right-0 top-full bg-white shadow rounded px-4 py-2 mt-2 animate-slide-down"
          >
            <span className="text-gray-800 font-medium">{email}</span>
            <button
              className="text-black hover:underline ml-2 cursor-pointer"
              onClick={toggleEmail}
            >
              Close
            </button>
            <button
              className="text-red-500 hover:underline ml-4 cursor-pointer"
              onClick={handleLogout}
            >
              Logout
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// App component: Main application component that includes video playback, transcript, search, summary, and chat features.
const App = ({ selectedOption, videoFile, userInput, account, summaries, titles, segments, transcript, Chunk_Transcript, Time_Stamp }) => {
  const [videoUrl, setVideoUrl] = useState(""); // State to manage the URL of the video to be processed
  const [file, setFile] = useState(null); // State to manage the selected file

  const handleLogout = () => {
    console.log("Logout clicked");
  };

  const [searchQuery, setSearchQuery] = useState(""); // State to manage the search query

  useEffect(() => {
    // Update video URL when a file is selected
    if (file) {
      const videoObjectURL = URL.createObjectURL(file);
      setVideoUrl(videoObjectURL);
    }
  }, [file, videoUrl]);

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-screen w-full">
      {/* Header section */}
      <div className="flex items-center justify-between bg-white shadow h-16 px-4">
        <div className="flex items-center">
          {account && (
            // Render back button if account exists
            <motion.button
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 flex items-center px-4 py-2 rounded mr-4"
              onClick={() => {
                navigate("/");
                console.log("Back clicked");
              }}
            >
              <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                <Icon icon={arrowLeft} className="h-5 w-5 mr-2" />
              </motion.div>
              <motion.span className="ml-2">Back </motion.span>
            </motion.button>
          )}
        </div>
        <span className="text-2xl font-bold text-gray-800"></span>
        <div className="flex items-center">
          {account && (
            // Render the WelcomeUsername component with user information
            <WelcomeUsername
              username={account.username}
              email={account.email}
              onLogout={handleLogout}
            />
          )}
        </div>
      </div>

      {/* Main content section */}
      <div className="container mx-auto p-4 grid grid-cols-2 grid-rows-[auto_1fr_auto] gap-8">
        {/* First row: Video player and transcript */}
        <div className="col-span-1 row-span-1 overflow-hidden">
          {selectedOption === "youtube" ? (
            <VideoPlayerYoutube userInput={userInput} />
          ) : (
            <VideoPlayerFile videoFile={videoFile} />
          )}
        </div>
        <div className="col-span-1 row-span-1 overflow-auto">
          {/* Display transcript with Chunk_Transcript and Time_Stamp */}
          <Transcript transcriptData={Chunk_Transcript} transcriptRef={Time_Stamp} maxTranscriptHeight={400} />
        </div>
        {/* Second row: Search bar */}
        <div className="col-span-1 row-span-1">
          <SearchBar onSearch={handleSearch} style={{ width: "80%" }} />
        </div>
        {/* Third row: Summary and QAChat components */}
        <div className="mt-0">
          <Summary
            searchQuery={searchQuery}
            summaries={summaries}
            titles={titles}
            segments={segments}
          />
        </div>
        <div className="col-span-1 row-span-1">
          <QAChat />
        </div>
      </div>
    </div>
  );
};



const Tool = () => {
  // State variables for managing the tool's form and data
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState(0);
  const [progressComplete, setProgressComplete] = useState(false);
  const [account, setAccount] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);
  const [error, setError] = useState("");
  const [videoFile, setVideoFile] = useState(null);
  const [userInput, setUserInput] = useState("");
  const [goToYoutube, setGoToYoutube] = useState(false);
  const [youtubeVal, setYoutubeVal] = useState("");
  const [Time_Stamp, setTime_Stamp] = useState([]);
  const [Chunk_Transcript, setChunk_Transcript] = useState(["Generating Transcript..."]);
  const [val, setVal] = useState("Upload file to generate transcripts");
  const [videoName, setVideoName] = useState("");

  // State variables related to file uploading
  const [filename, setFilename] = useState("");
  const [file, setFile] = useState(null);
  const [videoSrc, setVideoSrc] = useState("");
  const [goToFile, setGoToFile] = useState(false);

  // State variables related to video summarization
  const [length, setLength] = useState(0);
  const [summary, setSummary] = useState([]);
  const [segments, setSegments] = useState([]);
  const [titles, setTitles] = useState([]);
  const [quality, setQuality] = useState(null); // State for user option in case 0

  // Effect hook to check user authentication on component mount
  useEffect(() => {
    (async () => {
      try {
        const resp = await axiosJSON.get(`${global.config.path}/account`);
        setAccount(resp.data);
        if (resp.data) {
          setIsLoggedIn(true);
        }
      } catch (error) {
        console.log("Not authenticated");
      }
    })();
  }, []);

  // Function to handle moving to the next step in the form
  const handleNext = () => {
    setError(""); // Reset error message on each step change

    if (step === 0 && account) {
      // Save the user's option in case 0
      setQuality(selectedOption);
    }

    if (step === 0 && !account) {
      // If the user doesn't have an account, show a message
      alert("Please create an account first.");
      return;
    }

    if (step === 1 && !selectedOption) {
      // If the user hasn't selected an option, show a message
      setError("Please choose an option before proceeding.");
      return;
    }

    // Handling the YouTube upload step
    if (goToYoutube) {
      axiosJSON.post(`${global.config.path}/youtubeUpload`, {
        link: userInput,
        quality: quality // "high" or 'fast'
      })
      .then((res) => {
        let result = res.data;
        setYoutubeVal(result["Youtubetranscript"]);
        setTime_Stamp(result["First_timeStamp"]);
        setChunk_Transcript(result["Chunk_Transcript"]);
        setLength(result["Video_length"]);

        // Requesting summary for the uploaded video
        axiosJSON.post(`${global.config.path}/Summary`, {
          video_length: result["Video_length"],
          transcript_chunks: result["Chunk_Transcript"],
          transcript_text: result["Youtubetranscript"],
          quality: quality // "high" or 'fast'
        })
        .then((res) => {
          let result = res.data;
          setSummary(result["summaries"]);
          setSegments(result["segments"]);
          setTitles(result["segment_titles"]);
        });
      });
    }

    // Update step and progress state
    if (step < 2) {
      setProgress(progress + 25);
      setStep(step + 1);
    } else {
      setProgressComplete(true);
    }
  };

  // Animation style for a laser effect
  const laserEffectStyle = useSpring({
    boxShadow: `0 0 10px 5px rgba(0, 255, 0, ${progress / 100})`,
  });

  const navigate = useNavigate(); // Navigation function

  // Function to render content based on the current step
  const renderStepContent = () => {
    // Common styles for container
    const commonContainerStyles =
      "max-w-xl mx- bg-white rounded-xl shadow-md p-32 mb-8";

    let content = null;

    switch (step) {
      case 0:
        // Step 0 content
        content = (
          <div className="flex items-center justify-center bg-white">
            <div className={commonContainerStyles}>
              <h1 className="text-3xl font-bold text-center mb-8">LASER</h1>
              <p className="text-lg text-gray-600 text-center mb-6">
                Let's Get Started!
              </p>
              {account ? (
                // If user is logged in, show welcome and quality options
                <>
                  <p className="text-gray-600 mb-4">
                    Welcome back, {account.username}!
                  </p>
                  <p className="text-gray-600 mb-4">
                    Choose the segmentation quality:
                  </p>
                  <div className="flex justify-center space-x-6">
                    <button
                      className={`bg-gray-500 text-white py-3 px-6 rounded ${
                        selectedOption === "highQuality" && "bg-blue-400"
                      }`}
                      onClick={() => {
                        setSelectedOption("highQuality");
                      }}
                    >
                      High Quality
                    </button>
                    <button
                      className={`bg-gray-500 text-white py-3 px-6 rounded ${
                        selectedOption === "faster" && "bg-blue-400"
                      }`}
                      onClick={() => {
                        setSelectedOption("faster");
                      }}
                    >
                      Faster
                    </button>
                  </div>
                  {error && <p className="text-red-500 mt-4">{error}</p>}
                </>
              ) : (
                // If user is not logged in, prompt to create an account
                <div className="center">
                  <p className="text-gray-600 mb-4">
                    Create an account to proceed.
                  </p>
                  <div className="mx-auto">
                    <button
                      className="bg-gray-500 hover:bg-blue-300 text-white py-3 px-6 rounded-full mt-4"
                      onClick={() => {
                        navigate("/register");
                        console.log("Navigate to account creation");
                      }}
                    >
                      Create Account
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
        break;

      case 1:
        // Step 1 content
        content = (
          <div className={commonContainerStyles}>
            <h1 className="text-3xl font-bold text-center mb-4">
              Lecture Summarization
            </h1>
            <p className="text-lg text-gray-600 text-center mb-6">
              Choose an option before proceeding.
            </p>
            <div className="flex justify-center space-x-6">
              <button
                className={`bg-gray-500 text-white py-3 px-6 rounded ${
                  selectedOption === "youtube" && "bg-blue-400"
                }`}
                onClick={() => setSelectedOption("youtube")}
              >
                Paste YouTube Link
              </button>
              <button
                className={`bg-gray-500 text-white py-3 px-6 rounded ${
                  selectedOption === "upload" && "bg-blue-400"
                }`}
                onClick={() => setSelectedOption("upload")}
              >
                Upload File
              </button>
            </div>
          </div>
        );
        break;

      case 2:
        // Step 2 content
        content = (
          <div className={commonContainerStyles}>
            <h1 className="text-3xl font-bold text-center mb-4">
              Lecture Summarization
            </h1>
            <p className="text-lg text-gray-600 text-center mb-6">
              {selectedOption === "youtube"
                ? "Paste the YouTube link:"
                : "Upload the file:"}
            </p>
            {selectedOption === "youtube" && (
              <>
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => {
                    setUserInput(e.target.value);
                    setGoToYoutube(true);
                  }}
                  className="border border-gray-300 rounded p-3 mb-4 w-full"
                />
                {error && <p className="text-red-500 mb-4">{error}</p>}
              </>
            )}
            {selectedOption === "upload" && (
              <>
                <input
                  type="file"
                  accept="video/mp4"
                  className="border border-gray-300 rounded p-3 mb-4 w-full"
                  onChange={handleFileChange}
                />
                {error && <p className="text-red-500 mb-4">{error}</p>}
              </>
            )}
          </div>
        );
        break;

      case 3:
        // Step 3 content
        content = (
          <div className={commonContainerStyles}>
            <h1 className="text-3xl font-bold text-center mb-4">
              Lecture Summarization
            </h1>
            <p className="text-lg text-gray-600 text-center mb-6">
              Add a name for the video:
            </p>
            <input
              type="text"
              value={videoName}
              onChange={(e) => setVideoName(e.target.value)}
              className="border border-gray-300 rounded p-3 mb-4 w-full"
            />
            {error && <p className="text-red-500 mb-4">{error}</p>}
          </div>
        );
        break;

      default:
        break;
    }

    if (content && step !== 0) {
      // Add a divider after each step except Step 0
      content = (
        <>
          {content}
        </>
      );
    }

    return content;
  };

  // Function to handle going back to the previous step
  const handleBack = () => {
    setError(""); // Reset error message on going back

    if (step > 0) {
      setProgress(progress - 25); // Decrease progress by 50 for each step
      setStep(step - 1);
    }
  };

  // Function to handle navigating back to the home page
  const handleBackToHome = () => {
    navigate("/");
  }

  // Function to submit the file and handle the file change
  const handleFileSubmit = (file) => {
    const formData = new FormData();
    formData.append("file", file);

    // Post request to upload file
    axiosFILES.post('http://localhost:5000/upload', formData)
    .then((res) => {
      let result = res.data;
      setYoutubeVal(result["Youtubetranscript"]);
      setTime_Stamp(result["First_timeStamp"]);
      setChunk_Transcript(result["Chunk_Transcript"]);
      setLength(result["Video_length"]);

      // Post request for video summary
      axiosJSON.post(`${global.config.path}/Summary`, {
        video_length: result["Video_length"],
        transcript_chunks: result["Chunk_Transcript"],
        transcript_text: result["Youtubetranscript"],
        quality: quality // "high" or 'fast'
      })
      .then((res) => {
        let sum_res = res.data;
        setSummary(sum_res["summaries"]);
        setSegments(sum_res["segments"]);
        setTitles(sum_res["segment_titles"]);
        console.log(sum_res);
      });
    });
  };

  // Function to handle file change
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFile(file);
    setFilename(file.name);

    if (file && file.type === "video/mp4") {
      setVideoFile(URL.createObjectURL(file));
    } else {
      alert("Please choose a valid MP4 file.");
    }

    const url = URL.createObjectURL(file);
    setVideoSrc(url);
    setGoToFile(true);
    handleFileSubmit(file);
    console.log(url);
  };

  // Main render function
  return (
    <div className="flex items-center justify-center h-screen">
      {progressComplete ? (
        // Render the main application component when progress is complete
        <App
          selectedOption={selectedOption}
          videoFile={videoFile}
          userInput={userInput}
          account={account}
          summaries={summary}
          titles={titles}
          segments={segments}
          transcript={val}
          Chunk_Transcript={Chunk_Transcript}
          Time_Stamp={Time_Stamp}
        />
      ) : (
        // Render the form components
        <div>
          <div className="mt-4">{renderStepContent()}</div>
          {/* Back to home button */}
          <motion.button
            className="absolute top-4 left-4 bg-white p-2 rounded-full shadow-md"
            onClick={handleBackToHome}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.8 }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-gray-800"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
           <path
             strokeLinecap="round"
             strokeLinejoin="round"
             strokeWidth={2}
             d="M10 19l-7-7m0 0l7-7m-7 7h18"
           />
         </svg>
       </motion.button>
          <div className="mt-4">
            {step === 3 ? (
              <LoadingPage />
            ) : (
              <>
                <ProgressBar progress={progress} />
                <div
                  className="flex justify-between items-center mt-2"
                  style={laserEffectStyle}
                >
                  <p className="text-gray-600">{progress}%</p>
                  <div
                    style={{ display: "flex", justifyContent: "space-between" }}
                  >
                    {step > 0 ? (
                      <button
                        className="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-full"
                        onClick={handleBack}
                      >
                        Back
                      </button>
                    ) : (
                      <></>
                    )}

                    <button
                      className="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-full"
                      onClick={handleNext}
                    >
                      {step === 2 ? "Start Processing" : "Next"}
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Tool;
