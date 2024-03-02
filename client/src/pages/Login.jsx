// Importing necessary dependencies and modules
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axiosJSON from "../axiosJSON";
import { motion } from "framer-motion";
import login from "./assets/login.jpeg";

// Functional component definition for the Login page
const Login = () => {
  // State variables for email, password, authentication status, and user account
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false); // New state for authentication
  const [account, setAccount] = useState(null);

  // State variables for error and success messages
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Navigation hook for navigating between pages
  const navigate = useNavigate();

  // Function to handle user login
  const logInUser = () => {
    // Check if email and password are provided
    if (!email || !password) {
      setError("Email and password are required");
    } else {
      // Attempt to log in using axiosJSON to make a POST request
      axiosJSON
        .post(`${global.config.path}/login`, {
          email: email,
          password: password,
        })
        .then(function (response) {
          // If login is successful, update state and navigate to the "Tool" page
          setError("");
          setIsLoggedIn(true);
          setSuccessMessage("Logged in successfully!");
          navigate("/Tool");
        })
        .catch(function (error) {
          // Handle login error, show alert for invalid credentials
          console.log(error, "error");
          if (error.response && error.response.status === 401) {
            alert("Invalid credentials");
          }
        });
    }
  };

  // Function to handle navigation to the "Register" page
  const handleSignUp = () => {
    navigate("/register");
  };

  // Function to handle navigation back to the home page
  const handleBack = () => {
    navigate("/");
  };

  // Effect hook to check if the user is already authenticated on page load
  useEffect(() => {
    (async () => {
      try {
        // Make a GET request to retrieve user account information
        const resp = await axiosJSON.get(`${global.config.path}/account`);
        setAccount(resp.data);
        // If account data is received, set authentication status to true
        if (resp.data) {
          setIsLoggedIn(true);
        }
      } catch (error) {
        // Handle authentication error
        console.log("Not authenticated");
      }
    })();
  }, []);

  // Redirect to the account page if the user is already authenticated
  if (isLoggedIn) {
    navigate("/account");
    return null; // Prevent rendering the rest of the component
  }

  // JSX structure for the Login component with motion animations
  return (
    <div className="flex h-screen bg-white">
      {/* Left side with an image */}
      <div className="w-1/2 bg-[#ecf4f7] flex items-center justify-center">
        <motion.img
          className="w-3/4 h-3/4 object-cover"
          src={login}
          alt="Login"
        />
      </div>
      {/* Right side with login form */}
      <div className="w-1/2 bg-white p-10 mt-20">
        {/* Title with motion animation */}
        <motion.h1
          className="text-4xl font-bold text-gray-800 mb-6"
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          Log In to LASER
        </motion.h1>
        {/* Form with motion animation */}
        <motion.form
          className="space-y-4"
          onSubmit={logInUser}
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          {/* Email input */}
          <div>
            <label className="block text-gray-600 mb-2" htmlFor="email">
              Email
            </label>
            <input
              className="w-full border-2 border-gray-300 p-2 rounded-md focus:outline-none focus:border-blue-300"
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          {/* Password input */}
          <div>
            <label className="block text-gray-600 mb-2" htmlFor="password">
              Password
            </label>
            <input
              className="w-full border-2 border-gray-300 p-2 rounded-md focus:outline-none focus:border-blue-300"
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {/* Login button */}
          <div>
            <button
              className="w-full bg-blue-400 text-white p-3 rounded-md hover:bg-blue-600"
              type="button"
              onClick={() => logInUser()}
            >
              Log In
            </button>
          </div>
        </motion.form>
        {/* Message for signing up */}
        <motion.p
          className="mt-4 text-gray-600"
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          Don't have an account?{" "}
          <span
            className="text-blue-500 hover:underline"
            onClick={handleSignUp}
          >
            Sign Up
          </span>
        </motion.p>
      </div>
      {/* Back button with motion animation */}
      <motion.button
        className="absolute top-4 left-4 bg-white p-2 rounded-full shadow-md"
        onClick={handleBack}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
      >
        {/* SVG icon for back button */}
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
    </div>
  );
};

// Export the Login component as the default export
export default Login;