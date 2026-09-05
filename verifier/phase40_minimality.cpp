// Independent finite Phase 40 check: direct zero-position sums, not a DAG.
// All fixed-width arithmetic is explicitly bounded. For ell<=25,
// J<=3^(ell-1)<=3^24<2^39. The threshold table needs at most R=43;
// checked unsigned 128-bit powers cover every intermediate exactly.
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using u128 = unsigned __int128;

static u128 power(unsigned base, unsigned exponent) {
    u128 result = 1;
    const u128 maximum = ~u128(0);
    for (unsigned i=0; i<exponent; ++i) {
        if (result > maximum/base) throw std::overflow_error("exact power overflow");
        result *= base;
    }
    return result;
}

struct Tail {
    std::uint64_t jump;
    std::uint32_t mask;
    std::uint8_t weight;
    std::uint8_t minimum_run;
};

static std::string literal(std::uint32_t mask, unsigned ell) {
    std::string answer(ell, '0');
    for (unsigned j=0; j<ell; ++j)
        if (mask & (std::uint32_t(1) << (ell-j-1))) answer[j]='1';
    return answer;
}

struct Failure {
    bool found = false;
    Tail original{}, alternative{};
    unsigned gain=0, low=0, high=0;
};

static void emit_failure(const Failure &failure, unsigned ell) {
    if (!failure.found) { std::cout << "null"; return; }
    std::cout << "{\"original_tail\":\"" << literal(failure.original.mask,ell)
              << "\",\"alternative_tail\":\"" << literal(failure.alternative.mask,ell)
              << "\",\"J\":\"" << failure.original.jump
              << "\",\"gain\":" << failure.gain << ",\"Rlo\":" << failure.low
              << ",\"Rhi\":" << failure.high << ",\"original_Rmin\":"
              << unsigned(failure.original.minimum_run) << ",\"alternative_Rmin\":"
              << unsigned(failure.alternative.minimum_run) << '}';
}

int main(int argc, char **argv) {
    try {
        unsigned maximum_ell=25;
        if (argc==3 && std::string(argv[1])=="--max-tail-length") {
            std::string argument(argv[2]);
            if (argument.empty() || argument.find_first_not_of("0123456789")!=std::string::npos)
                throw std::invalid_argument("invalid exact finite bound");
            const auto parsed=std::stoul(argument);
            if (parsed<1 || parsed>25) throw std::invalid_argument("finite domain requires 1<=N<=25");
            maximum_ell=unsigned(parsed);
        } else if (argc!=1) throw std::invalid_argument("use --max-tail-length N");
        if (maximum_ell<1 || maximum_ell>25)
            throw std::invalid_argument("finite domain requires 1<=N<=25");

        unsigned threshold[26][26]{};
        for (unsigned length=1; length<=maximum_ell; ++length) {
            for (unsigned weight=0; weight<=length; ++weight) {
                unsigned run=1;
                while (power(3,run+weight)<=power(2,run+length)) {
                    if (++run>43) throw std::runtime_error("threshold bound violated");
                }
                threshold[length][weight]=run;
            }
        }
        std::uint64_t powers3[26]{1};
        for (unsigned j=1;j<=25;++j) powers3[j]=powers3[j-1]*3;
        std::cout << "{\"maximum_tail_length\":" << maximum_ell
                  << ",\"initial_run_bound\":null,\"threshold_table\":[";
        for (unsigned length=1;length<=maximum_ell;++length) {
            if (length>1) std::cout << ',';
            std::cout << '[';
            for (unsigned weight=0;weight<length;++weight) {
                if (weight) std::cout << ',';
                std::cout << threshold[length][weight];
            }
            std::cout << ']';
        }
        std::cout << "],\"levels\":[";
        for (unsigned ell=1;ell<=maximum_ell;++ell) {
            const std::uint32_t count=std::uint32_t(1) << (ell-1);
            std::vector<Tail> tails;
            tails.reserve(count);
            for (std::uint32_t mask=0;mask<count;++mask) {
                const unsigned weight=unsigned(__builtin_popcount(mask));
                unsigned suffix_ones=0, run=1;
                std::uint64_t jump=0;
                // j is a chronological position. Before each iteration,
                // suffix_ones counts the odd positions strictly after j.
                for (unsigned offset=0;offset<ell;++offset) {
                    const unsigned j=ell-offset-1;
                    run=std::max(run,threshold[j+1][weight-suffix_ones]);
                    if ((mask >> offset)&1U) ++suffix_ones;
                    else {
                        const std::uint64_t term=(std::uint64_t(1)<<j)*powers3[suffix_ones];
                        if (jump>std::numeric_limits<std::uint64_t>::max()-term)
                            throw std::overflow_error("jump sum overflow");
                        jump+=term;
                    }
                }
                if (jump>powers3[ell-1] || !(jump&1U) || suffix_ones!=weight)
                    throw std::runtime_error("closed-form jump bound/invariant violated");
                tails.push_back({jump,mask,std::uint8_t(weight),std::uint8_t(run)});
            }
            std::sort(tails.begin(),tails.end(),[](const Tail &a,const Tail &b) {
                return a.jump<b.jump || (a.jump==b.jump && a.mask<b.mask);
            });
            std::uint64_t vertices=0, collisions=0, pairs=0, failures=0, runs=0;
            Failure first;
            for (std::size_t begin=0;begin<tails.size();) {
                std::size_t end=begin+1;
                while (end<tails.size() && tails[end].jump==tails[begin].jump) ++end;
                ++vertices;
                if (end-begin>1) ++collisions;
                for (std::size_t i=begin;i<end;++i) {
                    for (std::size_t j=begin;j<end;++j) {
                        if (i!=j && tails[i].weight==tails[j].weight)
                            throw std::runtime_error("fixed-weight jump uniqueness violated");
                        if (tails[j].weight<=tails[i].weight) continue;
                        ++pairs;
                        const unsigned gain=tails[j].weight-tails[i].weight;
                        const unsigned low=std::max(unsigned(tails[i].minimum_run),gain+1);
                        const unsigned high=unsigned(tails[j].minimum_run)+gain-1;
                        if (low>high) continue;
                        ++failures;
                        runs+=high-low+1;
                        if (!first.found || tails[i].mask<first.original.mask ||
                            (tails[i].mask==first.original.mask && tails[j].mask<first.alternative.mask))
                            first={true,tails[i],tails[j],gain,low,high};
                    }
                }
                begin=end;
            }
            if (ell>1) std::cout << ',';
            std::cout << "{\"ell\":" << ell << ",\"tail_count\":" << count
                      << ",\"vertex_count\":" << vertices << ",\"collision_vertex_count\":" << collisions
                      << ",\"weight_gain_pair_count\":" << pairs << ",\"failing_pair_count\":" << failures
                      << ",\"failing_initial_run_count\":" << runs << ",\"first_failure\":";
            emit_failure(first,ell);
            std::cout << '}' << std::flush;
        }
        std::cout << "],\"proves_collatz\":false}\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "Phase 40 exact minimality check: " << error.what() << '\n';
        return 1;
    }
}
