#include "matlab_mex.hpp"

// -------------------------------------------------------------------------------------------------------
// Mex class to run Python function referenced in a global dictionary
// -------------------------------------------------------------------------------------------------------

class MexFunction : public matlab::mex::Function {
    public:
        void operator()(matlab::mex::ArgumentList outputs, matlab::mex::ArgumentList inputs) {
            if (inputs.size() < 1 || inputs[0].getType() != matlab::data::ArrayType::CHAR) {
                throw std::runtime_error("Input must be reference to a Python function."); }
            if (inputs.size() < 2 || inputs[1].getType() != matlab::data::ArrayType::UINT64) {
                throw std::runtime_error("Second input must be pointer to the converter."); }
            matlab::data::CharArray key = inputs[0];
            uintptr_t convfun = inputs[1][0];
            uintptr_t conv_addr = inputs[1][1];

            ((void(*)(const char *, uintptr_t, std::vector<matlab::data::Array>::iterator, size_t, matlab::data::Array *))convfun)
                (key.toAscii().c_str(), conv_addr, inputs.begin(), inputs.size(), &outputs[0]);
        }
};
