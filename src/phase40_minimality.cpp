// Forward shifted-correction DAG enumerator. Independent reverse-sum checker
// lives in verifier/. Packed integers are exact: J<=3^24<2^39, mask<2^24;
// threshold products below 3^68<2^108 fit checked unsigned __int128.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
using U = unsigned __int128;
struct Row { uint64_t j; uint32_t mask; uint8_t weight, need; };
std::string bits(uint32_t m, int ell) {
    std::string s(ell, '0');
    for(int i=ell-1;i>=1;--i) { s[i]=char('0'+(m&1));m>>=1; }
    return s;
}
int main(int argc,char**argv) {
    int maximum=argc==2?std::stoi(argv[1]):25;
    if(maximum<1 || maximum>25) throw std::runtime_error("domain 1..25 only");
    U p3[100];p3[0]=1;
    for(int i=1;i<=79;++i) { if(p3[i-1]>(~U(0))/3) throw std::runtime_error("overflow");p3[i]=p3[i-1]*3; }
    int need[26][26]{};
    for(int ell=1;ell<=maximum;++ell) for(int q=0;q<ell;++q) {
        int r=1;
        while(p3[r+q]<=(U(1)<<(r+ell))) ++r;
        if(r+q>68 || r+ell>=127) throw std::runtime_error("threshold bound");
        need[ell][q]=r;
    }
    std::vector<Row> rows{{1,0,0,uint8_t(need[1][0])}};
    std::cout<<"[";
    for(int ell=1;ell<=maximum;++ell) {
        std::sort(rows.begin(),rows.end(),[](auto&a,auto&b){return std::tie(a.j,a.mask)<std::tie(b.j,b.mask);});
        uint64_t vertices=0,collisions=0,pairs=0,failures=0,runs=0;
        bool found=false;Row f{},g{};int flo=0,fhi=0;
        for(size_t begin=0;begin<rows.size();) {
            size_t end=begin+1;while(end<rows.size()&&rows[end].j==rows[begin].j)++end;
            ++vertices;collisions+=end-begin>1;
            for(size_t a=begin;a<end;++a) for(size_t b=begin;b<end;++b) {
                int k=int(rows[b].weight)-rows[a].weight;if(k<=0)continue;
                ++pairs;
                int lo=std::max(int(rows[a].need),k+1),hi=int(rows[b].need)+k-1;
                if(lo>hi)continue;
                ++failures;runs+=hi-lo+1;
                if(!found || std::tie(rows[a].mask,rows[b].mask)<std::tie(f.mask,g.mask)) {
                    found=true;f=rows[a];g=rows[b];flo=lo;fhi=hi;
                }
            }
            begin=end;
        }
        if(ell>1)std::cout<<",";
        std::cout<<"{\"ell\":"<<ell<<",\"tail_count\":"<<rows.size()<<",\"vertex_count\":"<<vertices
                 <<",\"collision_vertex_count\":"<<collisions<<",\"weight_gain_pair_count\":"<<pairs
                 <<",\"failing_pair_count\":"<<failures<<",\"failing_initial_run_count\":"<<runs<<",\"first_failure\":";
        if(!found)std::cout<<"null";
        else std::cout<<"{\"original_tail\":\""<<bits(f.mask,ell)<<"\",\"alternative_tail\":\""<<bits(g.mask,ell)
            <<"\",\"J\":\""<<f.j<<"\",\"gain\":"<<int(g.weight-f.weight)<<",\"Rlo\":"<<flo<<",\"Rhi\":"<<fhi
            <<",\"original_Rmin\":"<<int(f.need)<<",\"alternative_Rmin\":"<<int(g.need)<<"}";
        std::cout<<"}"<<std::flush;
        if(ell<maximum) {
            std::vector<Row> next;next.reserve(rows.size()*2);
            for(auto row:rows) {
                next.push_back({row.j+(uint64_t(1)<<ell),row.mask*2,row.weight,uint8_t(std::max(int(row.need),need[ell+1][row.weight]))});
                next.push_back({row.j*3,row.mask*2+1,uint8_t(row.weight+1),uint8_t(std::max(int(row.need),need[ell+1][row.weight+1]))});
            }
            rows=std::move(next);
        }
    }
    std::cout<<"]\n";
}
