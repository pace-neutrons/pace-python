/* Own copy of mex.hpp and mexAdapter.hpp with only the functionality we need.
 * This enables compiling on github runners without loading Matlab
 */

// Uncomment to use the official interface
//#include "mex.hpp"
//#include "mexAdapter.hpp"

#include "load_matlab.hpp"
#include <cassert>
#include <cstdlib>
#include <MatlabDataArray/MDArray.hpp>

#ifndef mex_hpp
#define mex_hpp
#endif

#ifndef __MEX_CPP_PUBLISHED_API_HPP__
#define __MEX_CPP_PUBLISHED_API_HPP__

#if defined(_WIN32 )
#define NOEXCEPT throw()
#else
#define NOEXCEPT noexcept
#endif
#if defined(_MSC_VER) && _MSC_VER==1800
#define NOEXCEPT_FALSE throw(...)
#else
#define NOEXCEPT_FALSE noexcept(false)
#endif

#define __MEX_CPP_API__
#define __MEX_IO_ADAPTER_HPP__
#define __MEX_FUNCTION_CPP_HPP__
#define __MEX_EXCEPTION_CPP_HPP__

namespace matlab {
  namespace mex {
    template <typename iterator_type> class MexIORange {
        iterator_type begin_, end_;
        size_t size_;
        public:
        MexIORange(iterator_type b, iterator_type e, size_t size) : begin_(b), end_(e), size_(size) {}
        typename std::iterator_traits<iterator_type>::difference_type size() { return size_; }
        typename std::iterator_traits<iterator_type>::difference_type internal_size() { return std::distance(begin_, end_); }
        iterator_type begin() { return begin_; }
        iterator_type end() { return end_; }
        bool empty() { return size() == 0; }
        typename std::iterator_traits<iterator_type>::reference operator[](size_t i) {
            if (static_cast<int>(i) + 1 > internal_size())
                throw std::runtime_error("ArgumentList index out of range.");
            return *(begin_ + i);
        }
    };
    typedef MexIORange<std::vector<matlab::data::Array>::iterator> ArgumentList;
    class Function {
        void* functionImpl;
        public:
        Function() {
            const char* mlroot = std::getenv("LIBPYMCR_MATLAB_ROOT");
            _loadlibraries(mlroot);
            functionImpl = mexGetFunctionImpl();
        }
        virtual ~Function() NOEXCEPT_FALSE { mexDestroyFunctionImpl(functionImpl); }
        virtual void operator()(ArgumentList outputs, ArgumentList inputs) {}
    };
  } // matlab::mex
  namespace engine {
    class Exception : public std::exception {
        public:
        Exception() : std::exception() {}
        Exception(const std::string& msg) : message(msg) {}
        virtual ~Exception() {}
        Exception& operator=(const Exception& rhs) {
            message = rhs.message;
            return *this;
        }
        virtual const char* what() const NOEXCEPT { return message.c_str(); }
        private:
        std::string message;
    };
  } // matlab::engine
}
#endif // __MEX_CPP_PUBLISHED_API_HPP__

#ifndef __MEX_FILE_ADAPTER_HPP__
#define __MEX_FILE_ADAPTER_HPP__

#define __MEX_FUNCTION_ADAPTER_HPP__
#define __MEX_EXCEPTION_IMPL_CPP_HPP__

#ifdef _MSC_VER
# define DLLEXP __declspec(dllexport)
#elif __GNUC__ >= 4
# define DLLEXP __attribute__ ((visibility("default")))
#else
# define DLLEXP
#endif

void mexHandleException(void (*callbackErrHandler)(const char*, const char*)) {
    try {
        throw;
    } catch(const matlab::engine::Exception& ex) {
        callbackErrHandler(ex.what(), "");
    } catch(const matlab::Exception& ex) {
        callbackErrHandler(ex.what(), "");
    } catch(const std::exception& ex) {
        callbackErrHandler(ex.what(), "");
    } catch(...) {
        callbackErrHandler("Unknown exception thrown.", "");
    }
}

void implToArray(int na, void* va[], std::vector<matlab::data::Array>& pa) {
    assert(na == static_cast<int>(pa.capacity()));
    for(int i = 0; i < na; i++) {
        matlab::data::impl::ArrayImpl* impl = reinterpret_cast<matlab::data::impl::ArrayImpl*>(va[i]);
        pa.push_back(matlab::data::detail::Access::createObj<matlab::data::Array>(impl));
    }
}

void arrayToImpl(int na, void* va[], const std::vector<matlab::data::Array>& pa) {
    for(int i = 0; i < na; i++) {
        va[i] = matlab::data::detail::Access::getImpl<matlab::data::impl::ArrayImpl>(pa[i]);
    }
}

void arrayToImplOutput(int nlhs, std::vector<matlab::data::Array>& edi_plhs, void (*callbackOutput)(int, void**)) {
    assert(nlhs == static_cast<int>(edi_plhs.size()));
    std::unique_ptr<matlab::data::impl::ArrayImpl*, void(*)(matlab::data::impl::ArrayImpl**)>
        vlhsPtr(new matlab::data::impl::ArrayImpl*[nlhs],
                [](matlab::data::impl::ArrayImpl** ptr) {
                    delete[] ptr;
                });
    void** vlhs = (void**)vlhsPtr.get();
    arrayToImpl(nlhs, vlhs, edi_plhs);
    callbackOutput(nlhs, vlhs);
}

template <typename T> matlab::mex::Function * mexCreatorUtil() {
    static_assert(std::is_base_of<matlab::mex::Function, T>::value, "MexFunction class must be a subclass of matlab::mex::Function.");
    matlab::mex::Function* mexFunction = new T();
    return mexFunction;
}

class MexFunction; // This is defined by the user
// Define null function here for the old interface, else Win/Mac linker complains
extern "C" void mexFunction() {}

extern "C" DLLEXP void* mexCreateMexFunction(void (*callbackErrHandler)(const char*, const char*)) {
    try {
        matlab::mex::Function *mexFunc = mexCreatorUtil<MexFunction>();
        return mexFunc;
    } catch (...) {
        mexHandleException(callbackErrHandler);
        return nullptr;
    }
}

extern "C" DLLEXP void mexDestroyMexFunction(void* mexFunc,
                                             void (*callbackErrHandler)(const char*, const char*)) {
    matlab::mex::Function* mexFunction = reinterpret_cast<matlab::mex::Function*>(mexFunc);
    try {
        delete mexFunction;
    } catch (...) {
        mexHandleException(callbackErrHandler);
    }
}

extern "C" DLLEXP
void mexFunctionAdapter(int nlhs_,
                        int nlhs,
                        int nrhs,
                        void* vrhs[],
                        void* mFun,
                        void (*callbackOutput)(int, void**),
                        void (*callbackErrHandler)(const char*, const char*)) {
    matlab::mex::Function* mexFunction = reinterpret_cast<matlab::mex::Function*>(mFun);
    std::vector<matlab::data::Array> edi_prhs;
    edi_prhs.reserve(nrhs);
    implToArray(nrhs, vrhs, edi_prhs);
    std::vector<matlab::data::Array> edi_plhs(nlhs);
    matlab::mex::ArgumentList outputs(edi_plhs.begin(), edi_plhs.end(), nlhs_);
    matlab::mex::ArgumentList inputs(edi_prhs.begin(), edi_prhs.end(), nrhs);
    try {
        (*mexFunction)(outputs, inputs);
    } catch(...) {
        mexHandleException(callbackErrHandler);
        return;
    }
    arrayToImplOutput(nlhs, edi_plhs, callbackOutput);
}

#endif // __MEX_FILE_ADAPTER_HPP__
