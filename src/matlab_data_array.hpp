/* Own copy of MatlabDataArray.hpp with only the functionality we need.
 * This is to enable overrides of certain definitions.
 * Matlab on github-hosted action runners for MacOS X and Windows.
 */

#include <MatlabDataArray/ArrayFactory.hpp>
#include <MatlabDataArray/CharArray.hpp>
#include <MatlabDataArray/MDArray.hpp>
#include <MatlabDataArray/StructArray.hpp>
#include <MatlabDataArray/TypedArray.hpp>

#ifndef MARRAYFACTORY_HPP
#define MARRAYFACTORY_HPP
namespace matlab {
    namespace data {
        // The definition of the buffer_deleter_t type changed in R2024b when custom
        // deleters were enabled. We define our own so as to handle all Matlab versions
        template <typename T = void> using mbuffer_deleter_t = void(*)(T*);
        template <typename T> using mbuffer_ptr_t = std::unique_ptr<T[], mbuffer_deleter_t<T>>;

        // Subclass to overide the createBuffer method to have a consistent interface for <R2024b
        class mArrayFactory : public ArrayFactory {
        public:
            template <typename T> mbuffer_ptr_t<T> createBuffer(size_t numberOfElements) {
                void* buffer = nullptr;
                mbuffer_deleter_t<> deleter = nullptr;
                typedef int (*CreateBufferFcnPtr)(typename impl::ArrayFactoryImpl * impl, void** buffer,
                                                  void (**deleter)(void*), int dataType, size_t numElements);
                static const CreateBufferFcnPtr fcn =
                    detail::resolveFunction<CreateBufferFcnPtr>(detail::FunctionType::CREATE_BUFFER);
                detail::throwIfError(fcn(pImpl.get(), &buffer, &deleter,
                                         static_cast<int>(GetArrayType<T>::type), numberOfElements));
                return mbuffer_ptr_t<T>(static_cast<T*>(buffer), reinterpret_cast<mbuffer_deleter_t<T>>(deleter));
            }
            template <typename T> TypedArray<T> createArrayFromBuffer(ArrayDimensions dims, mbuffer_ptr_t<T> buffer, 
                                                                      MemoryLayout memoryLayout = MemoryLayout::COLUMN_MAJOR) {
                mbuffer_deleter_t<> deleter = reinterpret_cast<mbuffer_deleter_t<>>(buffer.get_deleter());
                impl::ArrayImpl* impl = nullptr;
                typedef int (*CreateArrayFromBufferV2FcnPtr)(typename impl::ArrayFactoryImpl * impl, int arrayType,
                        size_t* dims, size_t numDims, void* buffer, void (*deleter)(void*), typename impl::ArrayImpl**, int memoryLayout);
                static const CreateArrayFromBufferV2FcnPtr fcn = detail::resolveFunctionNoExcept<CreateArrayFromBufferV2FcnPtr>(
                        detail::FunctionType::CREATE_ARRAY_FROM_BUFFER_V2);
                if (fcn != nullptr) {
                    detail::throwIfError(fcn(pImpl.get(), static_cast<int>(GetArrayType<T>::type), &dims[0],
                                             dims.size(), buffer.release(), deleter, &impl, static_cast<int>(memoryLayout)));
                } else {
                // new version is not available; if asking for a row-major need to throw
                    if (memoryLayout == MemoryLayout::ROW_MAJOR) {
                        throw FeatureNotSupportedException(std::string("Row-major buffers require 2019a")); }
                    typedef int (*CreateArrayFromBufferFcnPtr)(typename impl::ArrayFactoryImpl * impl, int arrayType, size_t* dims,
                            size_t numDims, void* buffer, void (*deleter)(void*), typename impl::ArrayImpl**);
                    static const CreateArrayFromBufferFcnPtr fcn = detail::resolveFunction<CreateArrayFromBufferFcnPtr>(
                            detail::FunctionType::CREATE_ARRAY_FROM_BUFFER);
                    detail::throwIfError(fcn(pImpl.get(), static_cast<int>(GetArrayType<T>::type), &dims[0],
                                             dims.size(), buffer.release(), deleter, &impl));
                }
                return detail::Access::createObj<TypedArray<T>>(impl);
            }
        };
    }
}
#endif // MARRAYFACTORY_HPP
