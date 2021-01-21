#include "mex.hpp"
#include "mexAdapter.hpp"
#include <iostream>
#include <stdexcept>

using namespace matlab::data;
using matlab::mex::ArgumentList;

template <typename T> const void*
get_address_t(matlab::data::Array arr) {
    // We also need to use the iterator in TypedArray otherwise Matlab creates a temporary copy 
    // (like for indexing using the [] operator on the original Array object)
    // Needs to be const to avoid copying to a new (mutable) array
    const matlab::data::TypedArray<T> arr_t = matlab::data::TypedArray<T>(arr);
    const T &tmp = *arr_t.begin();
    return &tmp;
}


class MexFunction : public matlab::mex::Function {

    public:
        void operator()(ArgumentList outputs, ArgumentList inputs) {
            std::shared_ptr<matlab::engine::MATLABEngine> matlabPtr = getEngine();
            matlab::data::ArrayFactory factory;

            std::vector<double> addrs;
            for (auto arr: inputs) {
                const void *addr;
                if (arr.getType() == matlab::data::ArrayType::DOUBLE)
                    addr = get_address_t<double>(arr);
                else if (arr.getType() == matlab::data::ArrayType::SINGLE)
                    addr = get_address_t<float>(arr);
                else if (arr.getType() == matlab::data::ArrayType::COMPLEX_SINGLE)
                    addr = get_address_t<std::complex<float>>(arr);
                else if (arr.getType() == matlab::data::ArrayType::COMPLEX_DOUBLE)
                    addr = get_address_t<std::complex<double>>(arr);
                else
                    throw std::runtime_error("Unrecognised input type");
                addrs.push_back(double(reinterpret_cast<intptr_t>(addr)));
            }
            outputs[0] = factory.createArray<std::vector<double>::iterator, double>(std::vector<size_t>{addrs.size()}, addrs.begin(), addrs.end());
    }
};
