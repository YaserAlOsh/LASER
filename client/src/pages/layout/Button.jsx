import React from "react";

const Button = (props) => {
  return (
    <div>
      <button className="bg-blue-400 text-white p-3 rounded-md hover:bg-blue-600 py-2 px-5 mt-4 outline ">
        {props.title}
      </button>
    </div>
  );
};

export default Button;