import React from "react";
import Heading from "../layout/Heading";
import ReviewCard from "../layout/ReviewCard";
import profile from "../assets/profile.png";

const Reviews = () => {
  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center md:px-32 px-5">
      <Heading title1="Our" title2="Reviews" />

      <div className="flex flex-col md:flex-row gap-5 mt-5">
        <ReviewCard
          img={profile}
          name="Ahmed Abuassi"
          text="The website is really useful, especially for students to save time and get the essential information."
        />
        <ReviewCard
          img={profile}
          name="Malik Rajai Madi"
          text="The segments and the summaries were excellent even though at some points it was over detailed. I asked several questions, and he answered them all from what's given in the transcript; overall, it was an excellent experience and it's a very useful one."
        />
        <ReviewCard
          img={profile}
          name="Mustafa Sami"
          text="It was an amazing experience and it is very useful for studying when you are lazy to watch the whole video, especially when you have a final the next day."
        />
      </div>
    </div>
  );
};

export default Reviews;
