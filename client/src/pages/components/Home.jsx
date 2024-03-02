import React from "react";
import { motion } from "framer-motion";
import { NavLink } from "react-router-dom";
import Typewriter from "typewriter-effect";
import Button from "../layout/Button";
import img from "../assets/learning.jpeg";

const Home = () => {

  const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeInUp}
      className="min-h-[70vh] flex flex-col md:flex-row md:justify-between items-center md:mx-32 mx-5 mt-10"
    >
      <div className="md:w-2/4 text-center items-center">
        <h2 className="text-6xl font-semibold leading-tight">
          Learning with
          <span className="text-blue-400"> LASER</span>
        </h2>
        <h3 className="text-2xl leading-tight mt-8">
          AI-Based Tool For,
          <span style={{ marginLeft: "5px" }}>
            <Typewriter
              options={{
                strings: [
                  " Students",
                  " Educators",
                  " Learners",
                  "Everyone",
                ],
                autoStart: true,
                loop: true,
              }}
            />
          </span>
        </h3>

        <p className="text-lightText mt-10 text-start">
          <span className="text-blue-400"> LASER</span> — utilizes
          state-of-the-art AI models that have been specially designed <br />
          and fine-tuned for video lectures processing, and that can run at{" "}
          <span className="text-blue-400"> 100x </span>the efficiency of
          competitors.
        </p>
        <div className="mt-8">
          <NavLink to="/account" smooth={true} duration={500}>
            <Button title="Get Started" className="" />
          </NavLink>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-2/3 md:w-2/4 mt-8"
      >
        <img src={img} alt="Learning" />
      </motion.div>
    </motion.div>
  );
};

export default Home;