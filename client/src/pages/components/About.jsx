import React from "react";
import profile from "../assets/profile.png";
import Heading from "../layout/Heading";

const MemberCard = ({ name, position, img, description }) => {
  return (
    <div className="flex-shrink-0 bg-white p-6 rounded-lg shadow-md w-full md:w-96">
      <div className="relative overflow-hidden h-64 mb-4 rounded-md">
        <img
          src={img}
          alt={name}
          className="absolute inset-0 w-full h-full object-cover"
        />
      </div>
      <h2 className="text-xl font-semibold mb-2">{name}</h2>
      <p className="text-gray-500 mb-2">{position}</p>
      <p className="text-gray-700">{description}</p>
    </div>
  );
};

const About = () => {
  return (
    <>
      <div className="mt-20 flex flex-col items-center my-10 first-letter:">
        <Heading title1="The " title2="Team" />
      </div>
      <div className="flex flex-wrap justify-center gap-5 md:mx-32 mx-5 mt-14 mb-20">
        {/* Member 1 */}
        <MemberCard
          name="Yaser Haitham"
          position="Member 1"
          img={profile}
          description="A creative and detail-oriented individual with a strong foundation in software development. Has a particular interest in artificial intelligence and its applications in education. Known for their ability to think outside the box and come up with unique solutions to complex problems."
        />

        {/* Member 2 */}
        <MemberCard
          name="Meriem Aoudia"
          position="Member 2"
          img={profile}
          description="A highly motivated student with excellent research skills. Has a solid understanding of computer science principles and a passion for exploring new areas of technology. Brings a critical eye to the team, ensuring that all work is of the highest quality."
        />

        {/* Member 3 */}
        <MemberCard
          name="Osama Abdulghani"
          position="Member 3"
          img={profile}
          description="An innovative thinker with a strong background in data analysis and algorithm design. Has a deep understanding of computer systems and networks. Always eager to explore new technologies and methodologies to improve efficiency and effectiveness."
        />

        {/* Member 4 */}
        <MemberCard
          name="Omar Al-Ali"
          position="Member 4"
          img={profile}
          description="A dedicated and passionate computer science student with a knack for problem-solving. Has a keen interest in machine learning and has led several successful projects in the past. Brings a wealth of coding experience to the team, particularly in Python and Java."
        />
      </div>
    </>
  );
};

export default About;
