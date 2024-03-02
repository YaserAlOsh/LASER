import React from "react";
import Heading from "../layout/Heading";
import CoursesCard from "../layout/CoursesCard";
import F1 from "../assets/F1.jpeg";
import F2 from "../assets/F2.jpeg";
import F3 from "../assets/F3.jpeg";
import F4 from "../assets/F4.jpeg";
import F5 from "../assets/F5.jpeg";
import F6 from "../assets/F6.jpeg";

const Features = () => {
  return (
    <div className="min-h-screen flex flex-col items-center md:px-32 px-5 my-10">
      <Heading title1="Our" title2="Features" />

      <div className="flex flex-wrap justify-center gap-6 mt-6">
        {/* Top row */}
        <div className="flex justify-center gap-6">
          <CoursesCard img={F1} title="Summarize" text=" This feature allows you to get a quick overview of the lecture without having to watch the entire recording. It extracts the key points and presents them in a concise summary, saving you time and helping you focus on the most important information." />
          <CoursesCard img={F2} title="Segment" text="Break down your lecture recordings into manageable segments based on different topics discussed. This feature makes it easier to navigate through the lecture and review specific sections as needed."/>
          <CoursesCard img={F4} title="Transcript" text="Never miss a word with our transcript feature. It provides a written version of the lecture, allowing you to read along or review the content at your own pace."/>
        </div>

        {/* Bottom row */}
        <div className="flex justify-center gap-6 mt-6">
          <CoursesCard img={F3} title="Question Answer" text="Have a question while watching the lecture? This feature allows you to ask questions and get answers directly from the lecture content. It’s like having a personal tutor at your fingertips!"/>
          <CoursesCard img={F5} title="Download as PDF" text="Want to review the lecture offline or prefer reading on paper? This feature lets you download the lecture transcript as a PDF for easy access anytime, anywhere." />
          <CoursesCard img={F6} title="Save in Profile" text="Keep track of your progress and easily access your favorite lectures. With this feature, you can save lectures directly to your profile for quick retrieval and review later." />
        </div>
      </div>
    </div>
  );
};

export default Features;
