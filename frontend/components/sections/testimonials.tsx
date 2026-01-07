import React from 'react';
import Image from 'next/image';
import { ChevronRight } from 'lucide-react';

const testimonials = [
  {
    author: "NATHAN SOBO,",
    role: "CO-FOUNDER",
    company: "ZED INDUSTRIES",
    quote: "I want the best possible experience for our users, but also for our company. Baseten has hands down provided both. We really appreciate the level of commitment and support from your entire team.",
    image: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1753467615-nathan_headshot_2-24.jpeg",
    logoId: "zed",
    layout: "top-left"
  },
  {
    author: "SAHAJ GARG,",
    role: "CO-FOUNDER AND CTO",
    company: "WISPR",
    quote: "With Baseten, we gained a lot of control over our entire inference pipeline and worked with Baseten's team to optimize each step.",
    image: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1743642838-1638289677084-26.jpeg",
    logoId: "wispr",
    layout: "top-center"
  },
  {
    author: "MAHENDAN KARUNAKARAN,",
    role: "HEAD OF MOBILE ENGINEERING",
    company: "CLICKUP",
    quote: "With the launch of Brain MAX we've discovered how addictive speech-to-text is - we use it every day and want it everywhere. But it's difficult to get reliable, performant, and scalable inference. Baseten helped us unlock sub-300ms transcription with no unpredictable latency spikes. It's been a game-changer for us and our users.",
    image: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1762206077-mahendan_headshot-28.jpeg",
    logoId: "clickup",
    layout: "center-right"
  },
  {
    author: "ISAIAH GRANET,",
    role: "CEO AND CO-FOUNDER",
    company: "CLIENT",
    quote: "You guys have literally enabled us to hit insane revenue numbers without ever thinking about GPUs and scaling. We would be stuck in GPU AWS land without y'all. Truss files are amazing, y'all are on top of it always, and the product is well thought out. I know I ask for a lot so I just wanted to let you guys know that I am so blown away by everything Baseten.",
    image: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/8b29c68a-eaca-476e-a7ce-c0f16902fd64-baseten-co/assets/images/1708718045-isaiah-granet-headshot-30.png",
    logoId: "none",
    layout: "bottom-left"
  },
  {
    author: "WASEEM ALSHIKH,",
    role: "CTO AND CO-FOUNDER OF WRITER",
    company: "WRITER",
    quote: "Inference for custom-built LLMs could be a major headache. Thanks to Baseten, we're getting cost-effective high-performance model serving without any extra burden on our internal engineering teams. Instead, we get to focus our expertise on creating the best possible domain-specific LLMs for our customers.",
    image: "", // Placeholder or missing in assets
    logoId: "writer",
    layout: "bottom-right"
  }
];

const ZedLogo = () => (
  <div className="flex items-center gap-1.5">
    <div className="size-4 bg-black flex items-center justify-center">
      <div className="size-2.5 border border-white rotate-45"></div>
    </div>
    <span className="font-mono text-[10px] font-bold tracking-tight">ZED<br/>INDUSTRIES</span>
  </div>
);

const WisprLogo = () => (
  <div className="flex items-center gap-1">
    <div className="flex flex-col gap-[1px]">
      <div className="h-2.5 w-[2px] bg-black"></div>
      <div className="h-1.5 w-[2px] bg-black"></div>
    </div>
    <span className="font-mono text-[11px] font-bold">Wispr</span>
  </div>
);

const ClickUpLogo = () => (
  <div className="flex items-center gap-1">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L4.5 9.5 7 12l5-5 5 5 2.5-2.5L12 2zm0 14.5l-5-5-2.5 2.5L12 21.5l7.5-7.5-2.5-2.5-5 5z"/></svg>
    <span className="font-sans text-[11px] font-bold tracking-tight">ClickUp</span>
  </div>
);

export default function Testimonials() {
  return (
    <section className="bg-white py-24 md:py-32 overflow-hidden">
      <div className="container px-4 mx-auto max-w-[1296px]">
        <div className="relative grid grid-cols-1 md:grid-cols-12 gap-8 min-h-[1000px]">
          
          {/* Main Heading positioned specifically in the layout */}
          <div className="md:col-span-6 md:row-start-2 self-center z-10">
            <h2 className="text-[40px] md:text-[64px] font-semibold leading-[1.1] tracking-[-0.04em] text-[#0D0D0D] mb-6">
              What our customers<br />are saying
            </h2>
            <a 
              href="/resources/customers/" 
              className="inline-flex items-center gap-2 font-mono text-[12px] font-medium tracking-wider uppercase group"
            >
              See all
              <ChevronRight className="size-4 transition-transform group-hover:translate-x-1" />
            </a>
          </div>

          {/* Testimonials - Absolute and relative positioning applied based on visual staggered masonry-lite style */}
          
          {/* Nathan Sobo - Zed */}
          <div className="md:col-span-4 md:absolute md:top-0 md:left-0 max-w-[340px]">
            <div className="flex items-center gap-4 mb-5">
              <div className="relative size-12 overflow-hidden rounded-full shrink-0">
                <Image src={testimonials[0].image} alt="Nathan Sobo" fill className="object-cover" />
              </div>
              <div className="flex flex-col">
                <ZedLogo />
                <div className="font-mono text-[10px] text-[#737373] mt-1 tracking-wider uppercase">
                  {testimonials[0].author}<br/>{testimonials[0].role}
                </div>
              </div>
            </div>
            <blockquote className="text-[14px] leading-[1.6] text-[#0D0D0D] font-normal">
              &ldquo;{testimonials[0].quote}&rdquo;
            </blockquote>
          </div>

          {/* Sahaj Garg - Wispr */}
          <div className="md:col-span-4 md:absolute md:top-0 md:left-[45%] max-w-[340px]">
            <div className="flex items-center gap-4 mb-5">
              <div className="relative size-12 overflow-hidden rounded-full shrink-0">
                <Image src={testimonials[1].image} alt="Sahaj Garg" fill className="object-cover" />
              </div>
              <div className="flex flex-col">
                <WisprLogo />
                <div className="font-mono text-[10px] text-[#737373] mt-1 tracking-wider uppercase">
                  {testimonials[1].author}<br/>{testimonials[1].role}
                </div>
              </div>
            </div>
            <blockquote className="text-[14px] leading-[1.6] text-[#0D0D0D] font-normal">
              &ldquo;{testimonials[1].quote}&rdquo;
            </blockquote>
          </div>

          {/* Mahendan Karunakaran - ClickUp */}
          <div className="md:col-span-5 md:absolute md:top-[280px] md:right-0 max-w-[420px]">
            <div className="flex items-center gap-4 mb-5">
              <div className="relative size-12 overflow-hidden rounded-full shrink-0">
                <Image src={testimonials[2].image} alt="Mahendan Karunakaran" fill className="object-cover" />
              </div>
              <div className="flex flex-col">
                <ClickUpLogo />
                <div className="font-mono text-[10px] text-[#737373] mt-1 tracking-wider uppercase">
                  {testimonials[2].author}<br/>{testimonials[2].role}
                </div>
              </div>
            </div>
            <blockquote className="text-[14px] leading-[1.6] text-[#0D0D0D] font-normal">
              &ldquo;{testimonials[2].quote}&rdquo;
            </blockquote>
          </div>

          {/* Isaiah Granet */}
          <div className="md:col-span-4 md:absolute md:bottom-0 md:left-[45%] max-w-[420px]">
            <div className="flex items-center gap-4 mb-5">
              <div className="relative size-12 overflow-hidden rounded-full shrink-0 bg-gray-200">
                <Image src={testimonials[3].image} alt="Isaiah Granet" fill className="object-cover" />
              </div>
              <div className="flex flex-col">
                <div className="font-mono text-[10px] text-[#737373] tracking-wider uppercase">
                  {testimonials[3].author}<br/>{testimonials[3].role}
                </div>
              </div>
            </div>
            <blockquote className="text-[14px] leading-[1.6] text-[#0D0D0D] font-normal">
              &ldquo;{testimonials[3].quote}&rdquo;
            </blockquote>
          </div>

          {/* Waseem Alshikh - Writer */}
          <div className="md:col-span-4 md:absolute md:bottom-[40px] md:right-0 max-w-[420px]">
            <div className="flex items-center gap-4 mb-5">
              <div className="relative size-12 overflow-hidden rounded-full shrink-0 bg-slate-300 flex items-center justify-center text-xs font-mono text-white">
                WA
              </div>
              <div className="flex flex-col">
                <span className="font-mono text-[11px] font-bold tracking-tight">Writer</span>
                <div className="font-mono text-[10px] text-[#737373] mt-1 tracking-wider uppercase">
                  {testimonials[4].author}<br/>{testimonials[4].role}
                </div>
              </div>
            </div>
            <blockquote className="text-[14px] leading-[1.6] text-[#0D0D0D] font-normal">
              &ldquo;{testimonials[4].quote}&rdquo;
            </blockquote>
          </div>

        </div>
      </div>
    </section>
  );
}