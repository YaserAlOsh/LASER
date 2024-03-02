import React from "react";
import { Link } from "react-scroll";

const Footer = () => {
  return (
    <div>
      <div className=" flex flex-col md:flex-row justify-between bg-white border-2 border-lightText rounded-lg md:px-32 p-5">
        <div className="flex flex-col md:flex-row gap-5 font-medium p-1 text-lg">
          <Link
            to="home"
            spy={true}
            smooth={true}
            duration={500}
            className="hover:text-blue-400 transition-all cursor-pointer"
          >
            Home
          </Link>
          <Link
            to="about"
            spy={true}
            smooth={true}
            duration={500}
            className="hover:text-blue-400 transition-all cursor-pointer"
          >
            Team
          </Link>
          <Link
            to="courses"
            spy={true}
            smooth={true}
            duration={500}
            className="hover:text-blue-400 transition-all cursor-pointer"
          >
            Features
          </Link>
          <Link
            to="reviews"
            spy={true}
            smooth={true}
            duration={500}
            className="hover:text-blue-400 transition-all cursor-pointer"
          >
            Reviews
          </Link>

        </div>

        <div className=" mt-4 md:mt-0">
          <Link to="/" className=" font-semibold text-2xl p-1 cursor-pointer">
            LASER
          </Link>
        </div>
      </div>

      <div className=" text-center mt-4">
        <p>
          A Graduation Project Developed by the
          <span className="text-blue-400"> Senior Team </span>| All rights
          Reserved
        </p>
      </div>
    </div>
  );
};

export default Footer;
