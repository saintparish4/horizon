thought
import React from 'react';

/**
 * AnnouncementBar Component
 * 
 * Clones the bright green announcement bar at the top of the Baseten website.
 * Features:
 * - Solid #00FF7F (Mint Green) background
 * - Black monospaced uppercase text for the CTA
 * - Hover effects including arrow translation and text color persistence
 * - Responsive layout centering content on mobile/desktop
 */
const AnnouncementBar = () => {
  return (
    <div className="bg-[#00FF7F] w-full px-4 py-2 border-b border-black/5">
      <div className="max-w-[1296px] mx-auto flex flex-col md:flex-row md:items-center md:justify-center gap-2 text-[14px] md:text-[15px] font-sans text-[#0D0D0D] font-medium leading-relaxed">
        <span className="text-center md:text-left">
          Baseten acquires Parsed: Own your intelligence by unifying training and inference.
        </span>
        
        <a 
          href="https://www.baseten.co/blog/parsed-baseten"
          className="group inline-flex items-center justify-center gap-1 font-mono text-sm uppercase underline underline-offset-4 decoration-1 transition-colors duration-100 hover:text-[#0D0D0D]"
        >
          <span>READ</span>
          <svg 
            width="1.5em" 
            height="1.5em" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            className="size-4 transition-transform duration-150 ease-linear translate-y-[0.5px] group-hover:translate-x-[5px]"
          >
            <path d="M5 12h14m-7-7 7 7-7 7" />
          </svg>
        </a>
      </div>
    </div>
  );
};

export default AnnouncementBar;