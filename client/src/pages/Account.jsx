// Importing necessary dependencies and components
import { motion, AnimatePresence } from "framer-motion";
import { Icon } from "@iconify/react";
import chevronDown from "@iconify/icons-mdi/chevron-down";
import arrowLeft from "@iconify/icons-mdi/arrow-left";
import searchIcon from "@iconify/icons-mdi/magnify";
import empty from "./assets/404.jpeg";
import React, { useState, useEffect } from "react";
import "./pages_style/Account.css";
import axiosJSON from "../axiosJSON";
import axios from "axios";
import { useNavigate } from "react-router-dom";

// Custom hook for toggle functionality
const useToggle = (initialState = false) => {
  const [state, setState] = React.useState(initialState);
  const toggle = React.useCallback(() => setState((state) => !state), []);
  return [state, toggle];
};

// Component to display welcome message with username and email
const WelcomeUsername = ({ username, email, onLogout }) => {
  const [showEmail, toggleEmail] = useToggle();
  const [account, setAccount] = useState(null);

  // Function to handle logout
  const handleLogout = async () => {
    try {
      await axiosJSON.post(`${global.config.path}/logout`);
      setAccount(null);
      window.location.href = "/";
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  // Effect hook to fetch user account information
  useEffect(() => {
    (async () => {
      try {
        const resp = await axiosJSON.get(`${global.config.path}/account`);
        setAccount(resp.data);
      } catch (error) {
        console.log("Not authenticated");
      }
    })();
  }, []);

  // JSX structure for rendering welcome message with options to show email and logout
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

// Main Account component
const Account = () => {
  // State variables for account, videos, search query, selected video, and user
  const [account, setAccount] = useState(null);
  const [videos, setVideos] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [user, setUser] = useState(null);

  // Function to handle logout
  const handleLogout = async () => {
    try {
      await axiosJSON.post(`${global.config.path}/logout`);
      setAccount(null);
      window.location.href = "/";
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  // Function to handle search input change
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  // Function to handle search form submission
  const handleSearchSubmit = () => {
    axiosJSON
      .post(`${global.config.path}/mylectures/search`, {
        searchQuery: searchQuery,
      })
      .then((res) => {
        let result = res.data;
        console.log(result);
        let dataVideos = result.documents;
        let v_arr = [];
        for (let i = 0; i < dataVideos.length; i++) {
          let v = {
            'id': i,
            'link': dataVideos[i]['video_url'],
            'title': dataVideos[i]['video_name'],
            'date': dataVideos[i]['date'],
            'image': dataVideos[i]['thumbnail_image'],
            'transcriptUrl': dataVideos[i]['video_url'],
            'transcript': dataVideos[i]['video_transcript'],
            'summarizedContent': dataVideos[i]['summary']
          }
          v_arr.push(v);
        }
        setVideos(v_arr);
      });
  };

  // Effect hook to fetch user account information and videos
  useEffect(() => {
    (async () => {
      try {
        const resp = await axiosJSON.get(`${global.config.path}/account`);
        setUser(resp.data);
        setAccount(resp.data);

        const lectures = await axiosJSON.post(`${global.config.path}/mylectures`);

        let dataVideos = lectures.data.lectures;
        let v_arr = [];

        for (let i = 0; i < dataVideos.length; i++) {
          let v = {
            'id': i,
            'title': dataVideos[i]['video_name'],
            'link': dataVideos[i]['video_url'],
            'date': dataVideos[i]['date'],
            'image': dataVideos[i]['thumbnail_image'],
            'transcriptUrl': dataVideos[i]['video_url'],
            'transcript': dataVideos[i]['video_transcript'],
            'summarizedContent': dataVideos[i]['summary']
          }
          v_arr.push(v);
        }
        setVideos(v_arr);
      } catch (error) {
        console.log("Not authenticated");
      }
    })();
  }, []);

  // Function to handle video click
  const handleVideoClick = (videoId) => {
    setSelectedVideo(videoId);
  };

  // Page variants for motion animation
  const pageVariants = {
    initial: {
      opacity: 0,
      x: -100,
    },
    animate: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.5,
      },
    },
    exit: {
      opacity: 0,
      x: 100,
      transition: {
        duration: 0.5,
      },
    },
  };

  // Function to generate PDF from transcript and summary
  const generatePDF = async (transcript, summary, url) => {
    try {
      // Make a request to the server to generate the PDF
      const response = await axios.post('http://localhost:3000/generate_pdf', {
        transcript: transcript,
        summary: summary,
        title: url
      }, {
        responseType: 'arraybuffer',  // Ensure the response is treated as binary data
      });

      // Create a Blob from the PDF data
      const blob = new Blob([response.data], { type: 'application/pdf' });

      // Create a link element and trigger the download
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'LASER Summaries.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error generating PDF:', error);
    }
  };

  // Navigation function from react-router-dom
  const navigate = useNavigate();

  // JSX structure for rendering the Account component
  return (
    <motion.div
      className="flex flex-col h-screen bg-gray-100"
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      {/* Header section with back button, title, and user welcome message */}
      <div className="flex items-center justify-between bg-white shadow h-16 px-4">
        <div className="flex items-center">
          {account && (
            <motion.button
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 flex items-center px-4 py-2 rounded mr-4"
              onClick={() => {
                navigate('/Tool');
                console.log("Back clicked");
              }}
            >
              <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                <Icon icon={arrowLeft} className="h-5 w-5 mr-2" />
              </motion.div>
              <motion.span className="ml-2">Back to tool</motion.span>
            </motion.button>
          )}
        </div>
        <span className="text-2xl font-bold text-gray-800">Profile</span>
        <div className="flex items-center">
          {account && (
            <WelcomeUsername
              username={account.username}
              email={account.email}
              onLogout={handleLogout}
            />
          )}
        </div>
      </div>
      {/* Main content section */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Conditionally render if no account found */}
        {!account && (
          <div className="flex flex-col items-center justify-center h-full">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              No account found.
            </h2>
            <p className="text-gray-800 mb-4">
              It seems like you don't have an account. Create one now to start
              generating video summaries!
            </p>

            <button
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded"
              onClick={() => { navigate("/register") }}
            >
              Sign Up
            </button>
            <p className="text-gray-800 mt-4">
              Already have an account?{" "}
              <button
                className="text-blue-500 hover:underline ml-2 cursor-pointer"
                onClick={() => { navigate("/login") }}
              >
                Log In
              </button>
            </p>
          </div>
        )}

        {/* Conditionally render based on videos available */}
        {account && (
          <div>
            {/* Conditionally render if no videos found */}
            {videos.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full">
                <img
                  src={empty}
                  alt="No videos"
                  className="h-40 w-40 mb-4"
                />
                <h2 className="text-xl font-bold text-gray-800 text-center mb-4">
                  You haven't generated any video summaries yet.
                </h2>
                <button
                  className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded"
                  onClick={() => {
                    navigate('/Tool');
                    console.log("Start generating videos clicked");
                  }}
                >
                  Start Generating
                </button>
              </div>
            )}

           {/* Conditional rendering based on the presence of videos */}
      {videos.length > 0 && (
        <div>
          {/* Search bar */}
          <div className="mb-4 flex items-center">
            <input
              type="text"
              placeholder="Search videos..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="border border-gray-300 p-2 rounded mr-2"
            />
            <button
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded"
              onClick={handleSearchSubmit}
            >
              {/* Search icon */}
              <Icon icon={searchIcon} className="h-5 w-5" />
            </button>
          </div>

          {/* Section title */}
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            Your videos
          </h2>

          {/* Grid layout for displaying videos */}
          <div className="grid grid-cols-3 gap-4">
            {/* Mapping through videos array to render individual video items */}
            {videos.map((video) => (
              <motion.div
                key={video.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                className="bg-white shadow rounded-lg p-4 flex flex-col"
                onClick={() => handleVideoClick(video.id)}
                whileHover={{ cursor: 'pointer', scale: 1.05 }}
              >
                {/* Video thumbnail */}
                <img
                  src={`${global.config.path}/uploads/Accounts_images/${video.image}`}
                  alt={video.title}
                  className="h-40 w-full object-cover rounded"
                  onError={(e) =>
                    console.error('Error loading image:', e)
                  }
                />

                {/* Video details */}
                <h3 className="text-lg font-medium text-gray-800 mt-2">
                  {video.title}
                </h3>
                <span className="text-sm text-gray-600">
                  {video.date}
                </span>
                <p className="text-gray-800 flex-1 mt-2">
                  {/* Displaying a portion of the video transcript */}
                  {video.transcript
                    .split(/\s+/)
                    .slice(0, 10)
                    .join(' ')}
                </p>

                {/* Download transcript button */}
                <button
                  onClick={() =>
                    generatePDF(
                      video.transcript,
                      video.summarizedContent,
                      video.transcriptUrl
                    )
                  }
                  className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded mt-2 self-end"
                >
                  Download Transcript
                </button>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
    </div>
    </motion.div>
  );
};

export default Account;