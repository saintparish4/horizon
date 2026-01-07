import React from 'react';
import { ChevronRight } from 'lucide-react';

const FeatureCard = ({
  title,
  description,
  illustration,
  className = '',
}: {
  title: string;
  description: string;
  illustration: React.ReactNode;
  className?: string;
}) => (
  <div className={`flex flex-col border-dashed border-b md:border-b-0 ${className}`}>
    <div className="flex justify-between items-start mb-4">
      <h3 className="text-[20px] md:text-[24px] font-semibold tracking-[-0.03em] leading-tight max-w-[280px]">
        {title}
      </h3>
      <a
        href="#"
        className="flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.05em] text-muted-foreground hover:text-foreground transition-colors mt-1"
      >
        Learn more <ChevronRight className="size-3" />
      </a>
    </div>
    <p className="text-[15px] md:text-[16px] text-muted-foreground leading-relaxed mb-8 max-w-[420px]">
      {description}
    </p>
    <div className="relative w-full h-[240px] mt-auto flex items-center justify-center bg-transparent overflow-hidden">
      {illustration}
    </div>
  </div>
);

const TechnicalFeaturesGrid = () => {
  return (
    <section className="bg-[#FBFBFB] pt-24 pb-12 border-t border-dashed border-gray-200">
      <div className="container mx-auto px-4 lg:px-6">
        {/* Section Header */}
        <div className="max-w-3xl mb-16">
          <h2 className="text-[40px] md:text-[64px] font-semibold tracking-[-0.04em] leading-[1.1] mb-6">
            The fastest inference takes more than GPUs.
          </h2>
          <p className="text-[18px] md:text-[20px] text-muted-foreground leading-snug">
            Baseten delivers the infrastructure, tooling, and expertise needed to
            bring the most performant AI products to market—fast.
          </p>
        </div>

        {/* 2x2 Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2">
          {/* Top Left: Bleeding-edge performance */}
          <FeatureCard
            className="md:border-r md:border-b md:border-dashed p-0 md:pr-12 md:pb-12"
            title="Bleeding-edge performance research"
            description="Run cutting-edge performance research with custom kernels, the latest decoding techniques, and advanced caching baked into the Baseten Inference Stack."
            illustration={
              <div className="relative w-full h-full">
                {/* Abstract visualization - Nodes and connections */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full opacity-90 scale-110">
                  <div className="absolute top-[20%] left-[30%] w-16 h-16 bg-mint/20 border-2 border-mint rounded-sm rotate-12 flex items-center justify-center">
                    <div className="w-8 h-8 bg-mint/40 rotate-12" />
                  </div>
                  <div className="absolute top-[40%] left-[15%] w-12 h-12 bg-mint/10 border border-mint/40 rounded-sm -rotate-6" />
                  <div className="absolute top-[60%] left-[45%] w-20 h-20 bg-mint border-2 border-primary rounded-sm -rotate-3 overflow-hidden">
                    <div className="w-full h-full flex flex-col p-2 gap-1">
                      <div className="h-2 w-full bg-primary/20" />
                      <div className="h-2 w-2/3 bg-primary/20" />
                    </div>
                  </div>
                  <div className="absolute top-[30%] right-[20%] w-14 h-14 bg-lavender/30 border border-lavender rounded-sm rotate-45" />
                  {/* Dashed connecting lines represented by divs to mimic UI */}
                  <div className="absolute top-1/2 left-[20%] w-[60%] h-[1px] border-t border-dashed border-gray-300 -rotate-12 z-0" />
                  <div className="absolute top-[40%] left-[40%] w-[1px] h-[30%] border-l border-dashed border-gray-300 z-0" />
                  <div className="absolute bottom-[35%] right-[30%] px-2 py-1 bg-white border border-mint text-[10px] font-mono text-mint">
                    323MS TTFT
                  </div>
                </div>
              </div>
            }
          />

          {/* Top Right: Inference-optimized infra */}
          <FeatureCard
            className="md:border-b md:border-dashed p-0 md:pl-12 md:pb-12"
            title="Inference-optimized infrastructure"
            description="Scale workloads across any region and any cloud (in our cloud or yours), with blazing-fast cold starts and 99.99% uptime out of the box."
            illustration={
              <div className="relative w-full h-full flex items-center justify-center">
                <div className="relative">
                  {/* Concentric rings */}
                  <div className="w-48 h-48 border border-dashed border-gray-300 rounded-full flex items-center justify-center" />
                  <div className="absolute inset-0 m-auto w-36 h-36 border border-dashed border-gray-200 rounded-full" />
                  <div className="absolute inset-0 m-auto w-24 h-24 bg-mint/10 rounded-full flex items-center justify-center">
                    <div className="w-4 h-4 bg-primary rotate-45" />
                  </div>
                  {/* Floating icons/elements */}
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-white border border-gray-200 p-1.5 shadow-sm">
                    <div className="size-4 bg-mint/40" />
                  </div>
                  <div className="absolute bottom-4 -right-2 bg-white border-2 border-mint size-4 rounded-full" />
                  <div className="absolute top-1/4 -left-6 px-1.5 py-0.5 bg-white border border-gray-200 text-[9px] font-mono">
                    99.99% UPTIME
                  </div>
                </div>
              </div>
            }
          />

          {/* Bottom Left: DevEx */}
          <FeatureCard
            className="md:border-r md:border-dashed md:p-12 md:pl-0"
            title="DevEx built for rapid iteration"
            description="Deploy, optimize, and manage your models and compound AI with a delightful developer experience built into Baseten's inference platform."
            illustration={
              <div className="relative w-full h-full">
                <div className="absolute bottom-[20%] left-[10%] w-32 h-20 bg-white border border-gray-200 shadow-sm p-3">
                  <div className="flex gap-2 mb-2">
                    <div className="size-2 rounded-full bg-red-400" />
                    <div className="size-2 rounded-full bg-yellow-400" />
                    <div className="size-2 rounded-full bg-green-400" />
                  </div>
                  <div className="h-1 w-full bg-gray-100 mb-1" />
                  <div className="h-1 w-2/3 bg-gray-100" />
                </div>
                <div className="absolute top-[30%] right-[15%] w-24 h-24 bg-mint border-2 border-primary rotate-12 flex items-center justify-center">
                  <div className="font-mono text-[12px] text-primary font-bold">DEPLOY</div>
                </div>
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60%] h-[1px] border-t border-dashed border-gray-300 rotate-[35deg] z-0" />
              </div>
            }
          />

          {/* Bottom Right: Forward Deployed Engineers */}
          <FeatureCard
            className="md:border-dashed md:p-12 md:pr-0"
            title="Forward Deployed Engineers"
            description="Partner with our forward deployed engineers to build, optimize, and scale your models with hands-on support from prototype to production."
            illustration={
              <div className="relative w-full h-full flex items-center justify-center">
                <div className="relative w-40 h-40">
                  <div className="absolute inset-0 bg-mint/5 border border-dashed border-mint/30 rounded-lg -rotate-6" />
                  <div className="absolute inset-0 m-4 bg-white border-2 border-mint flex flex-col p-4 shadow-md">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="size-8 rounded-full bg-lavender/40" />
                      <div className="space-y-1">
                        <div className="h-1 w-12 bg-gray-200" />
                        <div className="h-1 w-8 bg-gray-100" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="h-1 w-full bg-mint/20" />
                      <div className="h-1 w-full bg-mint/20" />
                      <div className="h-1 w-3/4 bg-mint/20" />
                    </div>
                    <div className="mt-4 flex justify-end">
                      <div className="px-2 py-0.5 bg-mint text-[8px] font-mono uppercase">OPTIMIZING</div>
                    </div>
                  </div>
                </div>
              </div>
            }
          />
        </div>
      </div>
    </section>
  );
};

export default TechnicalFeaturesGrid;