import React from 'react';
import { ArrowRight, ChevronRight } from 'lucide-react';

const PerformancePlatform = () => {
  return (
    <section className="bg-[#FBFBFB] py-20 px-4 md:py-32 border-t border-dashed border-[#E5E7EB]">
      <div className="container mx-auto max-w-[1296px]">
        {/* Section Header */}
        <div className="flex flex-col items-center mb-24">
          <div className="mb-6">
            <span className="font-mono text-[10px] md:text-xs tracking-[0.1em] text-[#0D0D0D] border border-[#E5E7EB] px-3 py-1.5 uppercase bg-white">
              Products
            </span>
          </div>
          <h2 className="text-center max-w-4xl text-[#0D0D0D] leading-[1.1] tracking-[-0.04em]">
            The platform for <br />
            high-performance inference
          </h2>
        </div>

        {/* Feature Block 1: Dedicated Inference */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-px border border-dashed border-[#E5E7EB] mb-px">
          <div className="p-8 md:p-12 lg:p-16 flex flex-col justify-center border-b lg:border-b-0 lg:border-r border-dashed border-[#E5E7EB]">
            <h3 className="text-3xl md:text-4xl lg:text-5xl font-semibold leading-tight mb-8">
              Dedicated inference <br />
              <span className="relative inline-block">
                <span className="relative z-10">for high-scale workloads</span>
                <div className="absolute inset-0 bg-[#00FF7F] -left-2 -right-2 top-2 bottom-0 -z-0"></div>
              </span>
            </h3>
            <p className="text-[#0D0D0D] text-lg mb-10 max-w-md">
              Serve open-source, custom, and fine-tuned AI models on infra purpose-built for high-performance inference at massive scale.
            </p>
            <div className="flex flex-wrap gap-4">
              <a href="#" className="bg-black text-white font-mono text-xs tracking-wider px-6 py-4 uppercase flex items-center gap-2 hover:bg-[#00FF7F] hover:text-black transition-colors">
                Start Deploying <ChevronRight className="w-4 h-4" />
              </a>
              <a href="#" className="bg-white border border-black text-black font-mono text-xs tracking-wider px-6 py-4 uppercase flex items-center gap-2 hover:bg-[#F5F5F5] transition-colors">
                Learn More <ChevronRight className="w-4 h-4" />
              </a>
            </div>
          </div>
          <div className="bg-[#F5F5F5] min-h-[400px] flex items-center justify-center p-8 relative overflow-hidden">
            {/* Visual Placeholder for Instruction Diagram */}
            <div className="relative w-full h-full max-w-md aspect-square">
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-12 bg-white border border-[#E5E7EB] flex items-center justify-center font-mono text-[10px] uppercase shadow-sm z-20">
                Production
              </div>
              <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-40 h-40 rounded-full border border-dashed border-[#00FF7F]/30 animate-pulse"></div>
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col gap-2 scale-150">
                 <div className="w-32 h-6 bg-[#00FF7F]/40 rounded-full"></div>
                 <div className="w-32 h-6 bg-[#00FF7F]/20 rounded-full"></div>
                 <div className="w-32 h-6 bg-lavender/40 rounded-full"></div>
              </div>
              <div className="absolute bottom-12 right-4 bg-white border border-[#E5E7EB] p-2 font-mono text-[9px] uppercase space-y-1">
                <div className="flex justify-between gap-4"><span>Replicas</span><span className="text-[#00FF7F]">415</span></div>
                <div className="flex justify-between gap-4"><span>GPU Util</span><span className="text-[#00FF7F]">75%</span></div>
                <div className="flex justify-between gap-4"><span>TPS</span><span className="text-[#00FF7F]">93</span></div>
              </div>
            </div>
          </div>
        </div>

        {/* Split Section: Pre-optimized APIs & Training */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-px border-x border-b border-dashed border-[#E5E7EB]">
          {/* Left: Model APIs */}
          <div className="flex flex-col border-b lg:border-b-0 lg:border-r border-dashed border-[#E5E7EB]">
            <div className="p-8 md:p-12">
              <div className="flex items-center justify-between mb-6">
                <h4 className="text-xl font-semibold">Pre-optimized Model APIs</h4>
                <a href="#" className="font-mono text-[10px] uppercase flex items-center gap-1 hover:text-[#00FF7F] transition-colors">
                  Learn More <ChevronRight className="w-3 h-3" />
                </a>
              </div>
              <p className="text-sm text-[#737373] mb-12 max-w-sm">
                Test new workloads, prototype products, or evaluate the latest AI models optimized to be the fastest in production — instantly.
              </p>

              {/* Model Library List */}
              <div className="space-y-0.5">
                {[
                  { name: 'DeepSeek V3.2', action: 'Try it' },
                  { name: 'GPT OSS 120B', action: 'Try it' },
                  { name: 'Kimi K2 Thinking', action: 'Try it' },
                  { name: 'Explore the model Library', action: 'Explore', isMain: true }
                ].map((model, i) => (
                  <div key={i} className={`flex items-center justify-between p-4 bg-white border border-[#E5E7EB] hover:border-[#00FF7F] transition-colors group cursor-pointer ${model.isMain ? 'mt-4 border-dashed' : ''}`}>
                    <div className="flex items-center gap-4">
                      <div className={`w-6 h-6 rounded-sm ${i % 2 === 0 ? 'bg-[#00FF7F]/20' : 'bg-lavender/20'} flex items-center justify-center`}>
                        <div className={`w-2 h-2 rounded-full ${i % 2 === 0 ? 'bg-[#00FF7F]' : 'bg-lavender'}`}></div>
                      </div>
                      <span className={`text-sm tracking-tight ${model.isMain ? 'font-semibold' : 'font-medium'}`}>{model.name}</span>
                    </div>
                    <span className="font-mono text-[10px] uppercase flex items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                      {model.action} <ChevronRight className="w-3 h-3" />
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Training visualization */}
          <div className="flex flex-col">
            <div className="p-8 md:p-12">
              <div className="flex items-center justify-between mb-6">
                <h4 className="text-xl font-semibold">Run Training on Baseten</h4>
                <a href="#" className="font-mono text-[10px] uppercase flex items-center gap-1 hover:text-[#00FF7F] transition-colors">
                  Learn More <ChevronRight className="w-3 h-3" />
                </a>
              </div>
              <p className="text-sm text-[#737373] mb-12 max-w-sm">
                Train your models and easily deploy them in one click on inference-optimized infrastructure for the best possible performance.
              </p>

              {/* Training Visualization Diagram */}
              <div className="relative h-[280px] w-full flex items-center justify-center">
                <div className="absolute inset-0 dashed-grid opacity-30"></div>
                <div className="relative z-10 w-full max-w-xs flex flex-col items-center">
                  {/* Isometric Training Infra Illustration */}
                  <div className="relative">
                    <div className="w-32 h-16 bg-[#00FF7F]/10 border border-[#00FF7F]/30 rounded-full flex items-center justify-center">
                      <div className="w-24 h-10 bg-[#00FF7F]/40 rounded-full flex items-center justify-center border border-[#00FF7F]">
                        <span className="font-mono text-[9px] uppercase font-bold">Training Infra</span>
                      </div>
                    </div>
                    {/* Connecting lines */}
                    <div className="absolute -left-12 top-4 w-12 h-px bg-dashed border-t border-dashed border-[#E5E7EB]"></div>
                    <div className="absolute -right-12 top-4 w-12 h-px bg-dashed border-t border-dashed border-[#E5E7EB]"></div>
                    
                    {/* Data Node */}
                    <div className="absolute -left-20 top-2 bg-white border border-[#E5E7EB] px-2 py-1 font-mono text-[8px]">DATA</div>
                    
                    {/* Clusters */}
                    <div className="absolute bottom-[-60px] flex gap-3">
                       <div className="w-6 h-6 bg-[#00FF7F]/30 rotate-45 border border-[#00FF7F]/50"></div>
                       <div className="w-6 h-6 bg-lavender/30 rotate-45 border border-lavender/50 mt-4"></div>
                       <div className="w-6 h-6 bg-[#00FF7F]/60 rotate-45 border border-[#00FF7F]"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PerformancePlatform;