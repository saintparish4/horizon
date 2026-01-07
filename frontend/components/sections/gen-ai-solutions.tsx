import React from 'react';
import { ChevronRight } from 'lucide-react';

const GenAiSolutions = () => {
  return (
    <section className="bg-white py-[80px] lg:py-[120px] relative overflow-hidden">
      {/* Background Grid Pattern - Dashed */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.4]" 
           style={{ 
             backgroundImage: `linear-gradient(to right, #E5E7EB 1px, transparent 1px), linear-gradient(to bottom, #E5E7EB 1px, transparent 1px)`, 
             backgroundSize: '40px 40px',
             maskImage: 'linear-gradient(to bottom, transparent, black 10%, black 90%, transparent)'
           }}>
      </div>

      <div className="container relative z-10 mx-auto px-4 max-w-[1296px]">
        {/* Header Section */}
        <div className="max-w-4xl mx-auto text-center mb-16 lg:mb-20">
          <h2 className="text-[40px] lg:text-[64px] font-bold tracking-[-0.04em] leading-[1.1] mb-6 text-[#0D0D0D]">
            Engineered for the most<br className="hidden md:block" /> demanding Gen AI apps
          </h2>
          <p className="text-lg lg:text-xl text-[#737373] font-normal leading-[1.4] max-w-2xl mx-auto">
            Custom performance optimizations tailored for Gen AI applications are baked into the Baseten Inference Stack.
          </p>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 border-t border-l border-dashed border-[#E5E7EB]">
          
          {/* Rapid image generation */}
          <div className="p-8 lg:p-10 border-r border-b border-dashed border-[#E5E7EB] hover:bg-[#FBFBFB] transition-colors duration-300">
            <h3 className="text-xl font-bold tracking-tight mb-4 text-[#0D0D0D]">Rapid image generation</h3>
            <p className="text-sm lg:text-base text-[#737373] leading-relaxed">
              Serve custom models or ComfyUI workflows, fine-tune for your use case, and quickly generate high-quality images on our inference platform.
            </p>
          </div>

          {/* Optimized transcription */}
          <div className="p-8 lg:p-10 border-r border-b border-dashed border-[#E5E7EB] hover:bg-[#FBFBFB] transition-colors duration-300">
            <h3 className="text-xl font-bold tracking-tight mb-4 text-[#0D0D0D]">Optimized transcription</h3>
            <p className="text-sm lg:text-base text-[#737373] leading-relaxed">
              We power the fastest, most accurate, and most cost-efficient transcription and speaker diarization on the market.
            </p>
          </div>

          {/* SOTA text-to-speech */}
          <div className="p-8 lg:p-10 border-r border-b border-dashed border-[#E5E7EB] hover:bg-[#FBFBFB] transition-colors duration-300">
            <h3 className="text-xl font-bold tracking-tight mb-4 text-[#0D0D0D]">SOTA text-to-speech</h3>
            <p className="text-sm lg:text-base text-[#737373] leading-relaxed">
              We built real-time audio streaming to power AI phone calls, voice agents, translation, and more with the lowest time to first byte (TTFB).
            </p>
          </div>

          {/* Performant LLM runtimes */}
          <div className="p-8 lg:p-10 border-r border-b border-dashed border-[#E5E7EB] hover:bg-[#FBFBFB] transition-colors duration-300">
            <h3 className="text-xl font-bold tracking-tight mb-4 text-[#0D0D0D]">Performant LLM runtimes</h3>
            <p className="text-sm lg:text-base text-[#737373] leading-relaxed">
              Get the highest throughput and lowest latency in production with models like Qwen, DeepSeek, GLM, and gpt-oss.
            </p>
          </div>

          {/* The fastest embeddings */}
          <div className="p-8 lg:p-10 border-r border-b border-dashed border-[#E5E7EB] hover:bg-[#FBFBFB] transition-colors duration-300">
            <h3 className="text-xl font-bold tracking-tight mb-4 text-[#0D0D0D]">The fastest embeddings</h3>
            <p className="text-sm lg:text-base text-[#737373] leading-relaxed">
              Baseten Embeddings Inference (BEI) has over 2x higher throughput and 10% lower latency than any other solution on the market.
            </p>
          </div>

          {/* Ultra-low-latency compound AI */}
          <div className="p-8 lg:p-10 border-r border-b border-dashed border-[#E5E7EB] hover:bg-[#FBFBFB] transition-colors duration-300">
            <h3 className="text-xl font-bold tracking-tight mb-4 text-[#0D0D0D]">Ultra-low-latency compound AI</h3>
            <p className="text-sm lg:text-base text-[#737373] leading-relaxed">
              Baseten Chains enables granular hardware and autoscaling for compound AI, powering 6x better GPU usage and cutting latency in half.
            </p>
          </div>
        </div>

        {/* Footer Link / CTA inside grid layout wrapper */}
        <div className="mt-[-1px] border-l border-r border-b border-dashed border-[#E5E7EB]">
          <div className="flex flex-col md:flex-row items-center justify-between p-8 lg:p-10 gap-6">
            <div className="flex flex-col gap-2">
              <h3 className="text-xl font-bold tracking-tight text-[#0D0D0D]">Dedicated inference for custom models</h3>
              <p className="text-sm lg:text-base text-[#737373] max-w-2xl">
                Deploy any custom or proprietary model and get out-of-the-box model performance optimizations and massive horizontal scale with the Baseten Inference Stack.
              </p>
            </div>
            <a 
              href="https://docs.baseten.co" 
              className="group flex items-center gap-2 px-6 py-2 border border-[#E5E7EB] font-mono text-[12px] uppercase tracking-wider font-medium text-[#0D0D0D] hover:border-[#0D0D0D] transition-colors"
            >
              DOCS
              <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default GenAiSolutions;