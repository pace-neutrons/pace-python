#include "mex.hpp"
#include "mexAdapter.hpp"

using matlab::mex::ArgumentList;
class MexFunction : public matlab::mex::Function {
    matlab::data::ArrayFactory factory;
    public:
        void operator()(ArgumentList outputs, ArgumentList inputs) {
            void *mexfunimpl = mexGetFunctionImpl();
            void *engine = cppmex_getEngine(mexfunimpl);
            std::cout << "mexfunimpl = " << mexfunimpl << "\n";
            std::cout << "engine = " << engine << "\n";
            outputs[0] = factory.createScalar((uint64_t)engine);
        }
};
