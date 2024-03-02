import React, { useState } from "react";
import { AiOutlineMenu } from "react-icons/ai";
import { Link } from "react-scroll";
import logo from "../assets/main_logo.png";

const Navbar = () => {
  const [menu, setMenu] = useState(false);

  const handleChange = () => {
    setMenu(!menu);
  };

  return (
    <div>
      <div className="flex flex-row justify-between p-5 px-5 md:px-32 bg-white shadow-[0_3px_10px_rgb(0,0,0,0.2)]">
        <div className="flex items-center">
          <img
            src={logo}
            alt="Logo"
            className="mr-2"
            style={{ height: "70px", objectFit: "contain" }}
          />

          <Link to="/" className="font-semibold text-2xl p-1 cursor-pointer">
            
          </Link>
        </div>

        <nav className="hidden md:flex gap-5 font-medium p-1 text-lg">
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
        </nav>

        <div className="flex md:hidden" onClick={handleChange}>
          <div className="p-2">
            <AiOutlineMenu size={22} />
          </div>
        </div>
      </div>
      <div
        className={` ${
          menu ? "translate-x-0" : "-translate-x-full"
        } md:hidden flex flex-col absolute bg-black left-0 top-20 font-medium text-2xl text-center pt-8 pb-4 gap-8 w-full h-fit transition-transform duration-300 `}
      >
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
          About
        </Link>
        <Link
          to="features"
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
        <Link
          to="contact"
          spy={true}
          smooth={true}
          duration={500}
          className="hover:text-blue-400 transition-all cursor-pointer"
        >
          Contact
        </Link>
      </div>
    </div>
  );
};

export default Navbar;
