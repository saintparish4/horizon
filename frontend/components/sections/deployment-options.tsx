import React from 'react';
import { ChevronRight } from 'lucide-react';

/**
 * DeploymentOptions component clones the "Scale fast" section.
 * Includes a large radial arch background and comparison blocks for "Baseten Cloud" and "Self-hosted".
 * 
 * Theme: light
 */
export default function DeploymentOptions() {
  return (
    <section className="relative w-full bg-[#FBFBFB] py-20 lg:py-32 overflow-hidden">
      {/* Dashed background grid lines - replicating the blueprint feel */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="container h-full relative mx-auto max-w-[1296px]">
          <div className="absolute left-0 top-0 bottom-0 border-l border-dashed border-[#E5E7EB]" />
          <div className="absolute right-0 top-0 bottom-0 border-r border-dashed border-[#E5E7EB]" />
          <div className="absolute top-0 left-0 right-0 border-t border-dashed border-[#E5E7EB]" />
        </div>
      </div>

      <div className="container relative mx-auto max-w-[1296px] px-6">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mb-16 lg:mb-24">
          <div className="max-w-2xl">
            <h2 className="text-[40px] md:text-[64px] leading-[1.1] font-semibold tracking-tight text-[#0D0D0D] mb-6">
              Scale fast—in our cloud or yours.
            </h2>
            <p className="text-lg md:text-xl text-[#0D0D0D] max-w-xl leading-relaxed">
              Rapidly scale workloads across any cloud provider with global capacity. 
              We offer single-tenant and self-hosted deployments for extra security.
            </p>
          </div>
          
          <div>
            <a 
              href="#" 
              className="inline-flex items-center gap-2 bg-[#0D0D0D] text-white font-mono text-xs font-medium tracking-tight uppercase px-4 py-3 transition-colors hover:bg-[#00FF7F] hover:text-[#0D0D0D]"
            >
              LEARN MORE <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </div>

        {/* The large decorative radial arch background */}
        <div className="relative w-full aspect-[2/1] md:aspect-[3/1] flex justify-center items-end overflow-hidden mb-12">
          {/* Visual representation of the radial arc seen in the screenshots */}
          <div className="absolute top-1/2 w-[140%] aspect-square border border-dashed border-[#E5E7EB] rounded-full opacity-60" />
          <div className="absolute top-[60%] w-[110%] aspect-square border border-dashed border-[#E5E7EB] rounded-full opacity-40" />
          <div className="absolute top-[70%] w-[80%] aspect-square border border-dashed border-[#E5E7EB] rounded-full opacity-20" />
          
          {/* Gradient overlay to fade bottom */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#FBFBFB] via-transparent to-transparent pointer-events-none" />
        </div>

        {/* Comparison Blocks */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-[#E5E7EB] border border-[#E5E7EB]">
          {/* Baseten Cloud Card */}
          <div className="bg-[#FFFFFF] p-8 md:p-12 flex flex-col h-full gap-8">
            <div>
              <h3 className="text-xl font-semibold text-[#0D0D0D] mb-4">Baseten Cloud</h3>
              <p className="text-[#0D0D0D] text-base leading-relaxed opacity-80">
                Get the fastest time to market with fully-managed, global deployment options and massive horizontal scale. Use single-tenant clusters for additional workload isolation.
              </p>
            </div>
            <div className="mt-auto pt-6">
              <a 
                href="#" 
                className="inline-flex items-center gap-1 font-mono text-[12px] font-medium tracking-widest uppercase text-[#0D0D0D] hover:underline"
              >
                LEARN MORE <ChevronRight className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          {/* Self-hosted Card */}
          <div className="bg-[#FFFFFF] p-8 md:p-12 flex flex-col h-full gap-8">
            <div>
              <h3 className="text-xl font-semibold text-[#0D0D0D] mb-4">Self-hosted</h3>
              <p className="text-[#0D0D0D] text-base leading-relaxed opacity-80">
                Get the low latency, high throughput, and dev experience you expect from a managed service, right in your own VPCs. Optionally, go hybrid with on-demand flex capacity on Baseten Cloud.
              </p>
            </div>
            <div className="mt-auto pt-6">
              <a 
                href="#" 
                className="inline-flex items-center gap-1 font-mono text-[12px] font-medium tracking-widest uppercase text-[#0D0D0D] hover:underline"
              >
                LEARN MORE <ChevronRight className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}