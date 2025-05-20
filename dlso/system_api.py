import os
import shutil
import datetime
import hashlib
import zipfile
import tarfile


def file_opration(file_path:str, action:str=('read', 'write', 'append', 'delete', 'rename', 'move', 'copy', 'exists', 'info', 'hash'), content:str=None, new_path:str=None, hash_type:str='md5') -> dict:
    '''
    执行各种文件操作的统一接口函数，提供完整的文件管理能力。支持读写文件内容、复制移动文件、
    删除和重命名文件、检查文件是否存在、获取文件详细信息以及计算文件哈希值等操作。
    所有操作都返回统一格式的结果字典，包含操作状态和详细信息，便于程序处理。
    
    Args:
        file_path: 文件路径，可以是相对路径或绝对路径
        action: 操作类型，可选值为：
                read(读取): 读取文件内容
                write(写入): 覆盖写入内容到文件
                append(追加): 在文件末尾追加内容
                delete(删除): 删除指定文件
                rename(重命名): 重命名文件
                move(移动): 移动文件到新位置
                copy(复制): 复制文件到新位置
                exists(检查): 检查文件是否存在
                info(信息): 获取文件详细信息
                hash(哈希): 计算文件哈希值
        content: 写入或追加操作的内容，仅在write和append操作时使用
        new_path: 重命名、移动或复制操作的目标路径，仅在rename、move和copy操作时使用
        hash_type: 哈希算法类型，可选值为：md5, sha1, sha256, sha512（仅用于hash操作）
    
    Returns:
        返回包含操作结果的字典，常见字段说明：
        - success: 布尔值，操作是否成功
        - message: 字符串，结果描述信息
        
        特定操作返回的额外字段：
        - read: 添加content字段（文件内容）
        - write/append: 添加path字段（文件的绝对路径）
        - exists: 添加exists字段（布尔值，文件是否存在）
        - rename/move/copy: 添加source/old_path和destination/new_path字段（操作前后的文件路径）
        - info: 添加以下字段：
          - path: 文件的绝对路径
          - size: 文件大小（字节）
          - size_readable: 可读格式的文件大小（KB或MB）
          - is_file: 是否为文件
          - is_dir: 是否为目录
          - created_time: 创建时间
          - modified_time: 修改时间
          - accessed_time: 访问时间
          - permissions: 文件权限（八进制）
          - extension: 文件扩展名
        - hash: 添加以下字段：
          - hash_value: 计算得到的哈希值
          - hash_type: 使用的哈希算法
          - file_path: 文件的绝对路径
    
    Example:
        # 读取文件
        result = file_opration('/path/to/file.txt', 'read')
        if result['success']:
            content = result['content']
        
        # 写入文件
        result = file_opration('/path/to/file.txt', 'write', content='Hello World')
        
        # 获取文件信息
        result = file_opration('/path/to/file.txt', 'info')
        
        # 计算文件MD5值
        result = file_opration('/path/to/file.txt', 'hash', hash_type='md5')
        if result['success']:
            md5_value = result['hash_value']
    '''
    
    # 计算文件哈希值
    if action == 'hash':
        if not os.path.exists(file_path):
            return {
                'success': False,
                'message': f'文件 {file_path} 不存在，无法计算哈希值'
            }
        
        if not os.path.isfile(file_path):
            return {
                'success': False,
                'message': f'{file_path} 不是一个文件，无法计算哈希值'
            }
        
        try:
            # 根据指定的哈希类型选择算法
            if hash_type.lower() == 'md5':
                hash_algorithm = hashlib.md5()
            elif hash_type.lower() == 'sha1':
                hash_algorithm = hashlib.sha1()
            elif hash_type.lower() == 'sha256':
                hash_algorithm = hashlib.sha256()
            elif hash_type.lower() == 'sha512':
                hash_algorithm = hashlib.sha512()
            else:
                return {
                    'success': False,
                    'message': f'不支持的哈希算法类型: {hash_type}，支持的类型有: md5, sha1, sha256, sha512'
                }
            
            # 分块读取文件计算哈希值，避免大文件一次性加载到内存
            with open(file_path, 'rb') as f:
                # 每次读取 4MB 数据
                for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
                    hash_algorithm.update(chunk)
            
            # 获取十六进制格式的哈希值
            hash_value = hash_algorithm.hexdigest()
            
            return {
                'success': True,
                'message': f'已计算文件 {file_path} 的 {hash_type} 哈希值',
                'hash_type': hash_type.lower(),
                'hash_value': hash_value,
                'file_path': os.path.abspath(file_path)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'计算哈希值时出错: {str(e)}'
            }
    
    # 检查文件是否存在
    if action == 'exists':
        exists = os.path.exists(file_path)
        return {
            'success': True,
            'message': f"文件 {file_path} {'存在' if exists else '不存在'}",
            'exists': exists
        }
    
    # 获取文件信息
    if action == 'info':
        if not os.path.exists(file_path):
            return {
                'success': False,
                'message': f'文件 {file_path} 不存在，无法获取信息'
            }
        
        file_stat = os.stat(file_path)
        is_file = os.path.isfile(file_path)
        is_dir = os.path.isdir(file_path)
        
        # 格式化时间为易读的字符串
        created_time = datetime.datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        modified_time = datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        accessed_time = datetime.datetime.fromtimestamp(file_stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'success': True,
            'message': f'已获取文件 {file_path} 的信息',
            'path': os.path.abspath(file_path),
            'size': file_stat.st_size,
            'size_readable': f'{file_stat.st_size / 1024:.2f} KB' if file_stat.st_size < 1024 * 1024 else f'{file_stat.st_size / (1024 * 1024):.2f} MB',
            'is_file': is_file,
            'is_dir': is_dir,
            'created_time': created_time,
            'modified_time': modified_time,
            'accessed_time': accessed_time,
            'permissions': oct(file_stat.st_mode)[-3:],
            'extension': os.path.splitext(file_path)[1][1:] if os.path.splitext(file_path)[1] else ''
        }
    
    # 确保目录存在
    if action in ['write', 'append']:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # 确保目标目录存在（用于移动、复制操作）
    if action in ['rename', 'move', 'copy'] and new_path:
        os.makedirs(os.path.dirname(os.path.abspath(new_path)), exist_ok=True)
    
    try:
        if action == 'read':
            # 读取文件
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'message': f'错误：文件 {file_path} 不存在'
                }
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                'success': True,
                'message': f'文件 {file_path} 读取成功',
                'content': content
            }
        
        elif action == 'write':
            # 写入文件（覆盖）
            with open(file_path, 'w', encoding='utf-8') as f:
                if content is not None:
                    f.write(content)
            return {
                'success': True,
                'message': f'文件 {file_path} 写入成功',
                'path': os.path.abspath(file_path)
            }
        
        elif action == 'append':
            # 追加内容到文件
            with open(file_path, 'a', encoding='utf-8') as f:
                if content is not None:
                    f.write(content)
            return {
                'success': True,
                'message': f'内容已追加到文件 {file_path}',
                'path': os.path.abspath(file_path)
            }
        
        elif action == 'delete':
            # 删除文件
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    'success': True,
                    'message': f'文件 {file_path} 已删除'
                }
            return {
                'success': False,
                'message': f'文件 {file_path} 不存在，无法删除'
            }
        
        elif action == 'rename':
            # 重命名文件
            if not new_path:
                return {
                    'success': False,
                    'message': '重命名操作需要提供new_path参数'
                }
            if os.path.exists(file_path):
                os.rename(file_path, new_path)
                return {
                    'success': True,
                    'message': f'文件已从 {file_path} 重命名为 {new_path}',
                    'old_path': os.path.abspath(file_path),
                    'new_path': os.path.abspath(new_path)
                }
            return {
                'success': False,
                'message': f'文件 {file_path} 不存在，无法重命名'
            }
        
        elif action == 'move':
            # 移动文件
            if not new_path:
                return {
                    'success': False,
                    'message': '移动操作需要提供new_path参数'
                }
            if os.path.exists(file_path):
                shutil.move(file_path, new_path)
                return {
                    'success': True,
                    'message': f'文件已从 {file_path} 移动到 {new_path}',
                    'source': os.path.abspath(file_path),
                    'destination': os.path.abspath(new_path)
                }
            return {
                'success': False,
                'message': f'文件 {file_path} 不存在，无法移动'
            }
        
        elif action == 'copy':
            # 复制文件
            if not new_path:
                return {
                    'success': False,
                    'message': '复制操作需要提供new_path参数'
                }
            if os.path.exists(file_path):
                shutil.copy2(file_path, new_path)
                return {
                    'success': True,
                    'message': f'文件 {file_path} 已复制到 {new_path}',
                    'source': os.path.abspath(file_path),
                    'destination': os.path.abspath(new_path)
                }
            return {
                'success': False,
                'message': f'文件 {file_path} 不存在，无法复制'
            }
        
        else:
            return {
                'success': False,
                'message': f'不支持的操作: {action}'
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'文件操作错误: {str(e)}'
        }


def directory_operation(dir_path:str, action:str=('create', 'delete', 'list', 'exists', 'info', 'empty'), recursive:bool=False) -> dict:
    '''
    目录操作管理函数，提供全面的目录处理能力，包括创建、删除、列出内容、检查存在性及获取详情等功能。
    支持递归处理模式，可以深度遍历目录结构获取完整信息。所有操作均返回标准格式的结果字典，
    确保操作结果一致性和可预测性，方便程序进行后续处理和错误处理。
    
    Args:
        dir_path: 目录路径，可以是相对路径或绝对路径
        action: 操作类型，可选值为：
                create(创建): 创建新目录，如果目录已存在则不会报错
                delete(删除): 删除目录及其所有内容
                list(列出): 列出目录中的文件和子目录
                exists(检查): 检查目录是否存在
                info(信息): 获取目录的详细信息
                empty(清空): 删除目录中的所有内容但保留目录本身
        recursive: 是否递归处理子目录（仅适用于info和list操作）
                   - 当为True时，list操作会列出所有子目录及文件
                   - 当为True时，info操作会计算目录总大小并统计所有子目录和文件
    
    Returns:
        返回包含操作结果的字典，常见字段说明：
        - success: 布尔值，操作是否成功
        - message: 字符串，结果描述信息
        
        特定操作返回的额外字段：
        - create: 添加path字段（目录的绝对路径）
        - exists: 添加exists字段（布尔值，目录是否存在）
        - list: 添加以下字段：
          - files: 目录中的文件列表
          - dirs: 子目录列表
          - count: 包含files（文件数量）、dirs（子目录数量）和total（总项目数）的统计信息
        - info: 添加以下字段：
          - path: 目录的绝对路径
          - created_time: 创建时间
          - modified_time: 修改时间
          - accessed_time: 访问时间
          - permissions: 目录权限（八进制）
          - count: 一级子项统计（文件数、目录数、总数）
          - 当recursive=True时还会添加：
            - size: 目录总大小（字节）
            - size_readable: 可读格式的目录大小（KB或MB）
            - recursive_count: 包含所有子目录和文件的统计信息
    
    Example:
        # 检查目录是否存在
        result = directory_operation('/path/to/dir', 'exists')
        if result['exists']:
            print('目录存在')
        
        # 创建新目录
        result = directory_operation('/path/to/new_dir', 'create')
        
        # 列出目录内容（仅一级）
        result = directory_operation('/path/to/dir', 'list')
        if result['success']:
            files = result['files']  # 文件列表
            dirs = result['dirs']    # 目录列表
        
        # 递归列出目录所有内容
        result = directory_operation('/path/to/dir', 'list', recursive=True)
        
        # 获取目录详细信息（包括大小计算）
        result = directory_operation('/path/to/dir', 'info', recursive=True)
    '''
    
    # 检查目录是否存在
    if action == 'exists':
        exists = os.path.exists(dir_path) and os.path.isdir(dir_path)
        return {
            'success': True,
            'message': f"目录 {dir_path} {'存在' if exists else '不存在'}",
            'exists': exists
        }
    
    # 创建目录
    elif action == 'create':
        try:
            os.makedirs(dir_path, exist_ok=True)
            return {
                'success': True,
                'message': f'目录 {dir_path} 创建成功',
                'path': os.path.abspath(dir_path)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'创建目录失败: {str(e)}'
            }
    
    # 删除目录
    elif action == 'delete':
        if not os.path.exists(dir_path):
            return {
                'success': False,
                'message': f'目录 {dir_path} 不存在，无法删除'
            }
        
        if not os.path.isdir(dir_path):
            return {
                'success': False,
                'message': f'{dir_path} 不是一个目录'
            }
        
        try:
            shutil.rmtree(dir_path)
            return {
                'success': True,
                'message': f'目录 {dir_path} 已删除'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'删除目录失败: {str(e)}'
            }
    
    # 列出目录内容
    elif action == 'list':
        if not os.path.exists(dir_path):
            return {
                'success': False,
                'message': f'目录 {dir_path} 不存在'
            }
        
        if not os.path.isdir(dir_path):
            return {
                'success': False,
                'message': f'{dir_path} 不是一个目录'
            }
        
        try:
            result = {
                'success': True,
                'message': f'已列出目录 {dir_path} 的内容',
                'files': [],
                'dirs': [],
                'count': {}
            }
            
            if recursive:
                # 递归列出所有子目录和文件
                all_files = []
                all_dirs = []
                
                for root, dirs, files in os.walk(dir_path):
                    # 转换为相对路径
                    rel_root = os.path.relpath(root, dir_path)
                    if rel_root == '.':
                        # 当前目录下的文件直接添加
                        all_files.extend(files)
                        all_dirs.extend(dirs)
                    else:
                        # 子目录下的文件添加相对路径
                        all_files.extend([os.path.join(rel_root, f) for f in files])
                        all_dirs.extend([os.path.join(rel_root, d) for d in dirs])
                
                result['files'] = all_files
                result['dirs'] = all_dirs
                result['count'] = {
                    'files': len(all_files),
                    'dirs': len(all_dirs),
                    'total': len(all_files) + len(all_dirs)
                }
                result['message'] = f'已递归列出目录 {dir_path} 的所有内容'
            else:
                # 仅列出当前目录内容
                items = os.listdir(dir_path)
                files = []
                dirs = []
                
                for item in items:
                    item_path = os.path.join(dir_path, item)
                    if os.path.isfile(item_path):
                        files.append(item)
                    elif os.path.isdir(item_path):
                        dirs.append(item)
                
                result['files'] = files
                result['dirs'] = dirs
                result['count'] = {
                    'files': len(files),
                    'dirs': len(dirs),
                    'total': len(items)
                }
            
            return result
        except Exception as e:
            return {
                'success': False,
                'message': f'列出目录内容失败: {str(e)}'
            }
    
    # 获取目录信息
    elif action == 'info':
        if not os.path.exists(dir_path):
            return {
                'success': False,
                'message': f'目录 {dir_path} 不存在'
            }
        
        if not os.path.isdir(dir_path):
            return {
                'success': False,
                'message': f'{dir_path} 不是一个目录'
            }
        
        try:
            dir_stat = os.stat(dir_path)
            
            # 格式化时间
            created_time = datetime.datetime.fromtimestamp(dir_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            modified_time = datetime.datetime.fromtimestamp(dir_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            accessed_time = datetime.datetime.fromtimestamp(dir_stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')
            
            result = {
                'success': True,
                'message': f'已获取目录 {dir_path} 的基本信息',
                'path': os.path.abspath(dir_path),
                'created_time': created_time,
                'modified_time': modified_time,
                'accessed_time': accessed_time,
                'permissions': oct(dir_stat.st_mode)[-3:],
            }
            
            # 获取一级目录内容统计
            try:
                items = os.listdir(dir_path)
                files = []
                dirs = []
                
                for item in items:
                    item_path = os.path.join(dir_path, item)
                    if os.path.isfile(item_path):
                        files.append(item)
                    elif os.path.isdir(item_path):
                        dirs.append(item)
                
                result['count'] = {
                    'files': len(files),
                    'dirs': len(dirs),
                    'total': len(items)
                }
            except:
                result['count'] = {'error': '无法读取目录内容'}
            
            # 只有当用户明确请求递归时才计算完整大小
            if recursive:
                result['message'] = f'已获取目录 {dir_path} 的详细信息（递归）'
                result['recursive'] = True
                
                try:
                    # 计算目录大小和内容数量
                    total_size = 0
                    file_count = 0
                    dir_count = 0
                    
                    for root, dirs, files in os.walk(dir_path):
                        dir_count += len(dirs)
                        file_count += len(files)
                        for file in files:
                            file_path = os.path.join(root, file)
                            if os.path.exists(file_path):  # 避免符号链接引起的问题
                                total_size += os.path.getsize(file_path)
                    
                    # 格式化大小
                    size_readable = f'{total_size / 1024:.2f} KB' if total_size < 1024 * 1024 else f'{total_size / (1024 * 1024):.2f} MB'
                    
                    result['size'] = total_size
                    result['size_readable'] = size_readable
                    result['recursive_count'] = {
                        'files': file_count,
                        'dirs': dir_count,
                        'total': file_count + dir_count
                    }
                except Exception as e:
                    result['size_error'] = f'计算递归大小时出错: {str(e)}'
            
            return result
        except Exception as e:
            return {
                'success': False,
                'message': f'获取目录信息失败: {str(e)}'
            }
    
    # 清空目录
    elif action == 'empty':
        if not os.path.exists(dir_path):
            return {
                'success': False,
                'message': f'目录 {dir_path} 不存在'
            }
        
        if not os.path.isdir(dir_path):
            return {
                'success': False,
                'message': f'{dir_path} 不是一个目录'
            }
        
        try:
            # 删除目录中的所有内容，但保留目录本身
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            
            return {
                'success': True,
                'message': f'目录 {dir_path} 已清空'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'清空目录失败: {str(e)}'
            }
    
    else:
        return {
            'success': False,
            'message': f'不支持的操作: {action}'
        }


def archive_operation(source_paths:list|str, output_path:str, action:str=('compress','decompress'), format:str=('zip','tar','gztar','bztar','xztar')) -> dict:
    '''
    文件压缩与解压缩操作函数，提供多种压缩格式支持和灵活的文件处理能力。
    支持将单个或多个文件/目录压缩为常见压缩格式，或将压缩文件解压到指定目录。
    自动处理路径创建、格式识别和错误处理，确保操作安全稳定，适用于备份、分发和归档等场景。
    
    Args:
        source_paths: 源文件路径
            - 压缩时：可以是文件/目录路径的列表或单个文件/目录路径
            - 解压缩时：必须是单个压缩文件的路径
        output_path: 输出路径
            - 压缩时：压缩文件的保存路径（包含文件名）
            - 解压缩时：解压目标目录
        action: 操作类型，可选值为：
            - compress(压缩)：将源文件/目录压缩成压缩文件
            - decompress(解压缩)：将压缩文件解压到目标目录
        format: 压缩格式，可选值为：
            - zip：ZIP格式 (.zip)
            - tar：TAR格式 (.tar)
            - gztar：GZIP压缩的TAR格式 (.tar.gz, .tgz)
            - bztar：BZIP2压缩的TAR格式 (.tar.bz2, .tbz2)
            - xztar：LZMA压缩的TAR格式 (.tar.xz, .txz)
            若为None，则会根据output_path的扩展名自动选择格式，如无法识别则默认使用zip
    
    Returns:
        返回包含操作结果的字典，常见字段说明：
        - success: 布尔值，操作是否成功
        - message: 字符串，结果描述信息
        
        压缩操作成功时返回的额外字段：
        - archive_path: 生成的压缩文件的绝对路径
        - format: 使用的压缩格式
        
        解压缩操作成功时返回的额外字段：
        - extract_dir: 解压目标目录的绝对路径
        - format: 识别的压缩格式
    
    Example:
        # 压缩单个目录
        result = archive_operation('/path/to/folder', '/path/to/archive.zip', 'compress')
        
        # 压缩多个文件到tar.gz格式
        result = archive_operation(
            ['/path/file1.txt', '/path/file2.jpg', '/path/folder'], 
            '/path/to/archive.tar.gz', 
            'compress'
        )
        
        # 解压缩文件到指定目录
        result = archive_operation('/path/to/archive.zip', '/path/to/extract_folder', 'decompress')
    '''
    
    # 确保源路径是列表类型
    if isinstance(source_paths, str):
        source_paths = [source_paths]
    
    # 确保目标目录存在
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # 压缩操作
    if action == 'compress':
        try:
            # 根据输出路径或指定格式确定压缩格式
            if format is None:
                # 根据扩展名自动判断格式
                ext = os.path.splitext(output_path)[1].lower()
                if ext == '.zip':
                    format = 'zip'
                elif ext == '.tar':
                    format = 'tar'
                elif ext in ('.tar.gz', '.tgz'):
                    format = 'gztar'
                elif ext in ('.tar.bz2', '.tbz2'):
                    format = 'bztar'
                elif ext in ('.tar.xz', '.txz'):
                    format = 'xztar'
                else:
                    # 默认使用zip格式
                    format = 'zip'
                    if not output_path.lower().endswith('.zip'):
                        output_path += '.zip'
            
            # 检查所有源路径是否存在
            missing_paths = [path for path in source_paths if not os.path.exists(path)]
            if missing_paths:
                return {
                    'success': False,
                    'message': f"以下文件或目录不存在: {', '.join(missing_paths)}"
                }
            
            # 使用shutil.make_archive进行压缩（单个目录情况）
            if len(source_paths) == 1 and os.path.isdir(source_paths[0]):
                base_name = os.path.splitext(output_path)[0]  # 移除扩展名
                result_path = shutil.make_archive(
                    base_name=base_name,
                    format=format,
                    root_dir=os.path.dirname(source_paths[0]),
                    base_dir=os.path.basename(source_paths[0])
                )
                return {
                    'success': True,
                    'message': f"目录 {source_paths[0]} 已压缩为 {result_path}",
                    'archive_path': result_path,
                    'format': format
                }
            
            # 处理多个文件/目录或单个文件情况
            if format == 'zip':
                # 使用zipfile模块创建ZIP文件
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for path in source_paths:
                        if os.path.isfile(path):
                            # 添加单个文件
                            zipf.write(path, os.path.basename(path))
                        else:
                            # 添加目录及其所有内容
                            for root, _, files in os.walk(path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    # 计算相对路径
                                    arcname = os.path.join(os.path.basename(path), os.path.relpath(file_path, os.path.dirname(path)))
                                    zipf.write(file_path, arcname)
            else:
                # 对于tar格式，使用tarfile模块
                mode = {
                    'tar': 'w',
                    'gztar': 'w:gz',
                    'bztar': 'w:bz2',
                    'xztar': 'w:xz'
                }.get(format, 'w')
                
                with tarfile.open(output_path, mode) as tarf:
                    for path in source_paths:
                        if os.path.isfile(path):
                            # 添加单个文件
                            tarf.add(path, os.path.basename(path))
                        else:
                            # 添加目录及其所有内容
                            tarf.add(path, os.path.basename(path))
            
            return {
                'success': True,
                'message': f"{len(source_paths)}个文件/目录已压缩为 {output_path}",
                'archive_path': os.path.abspath(output_path),
                'format': format
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"压缩操作失败: {str(e)}"
            }
    
    # 解压缩操作
    elif action == 'decompress':
        # 解压缩时source_paths应该只有一个元素
        if len(source_paths) != 1:
            return {
                'success': False,
                'message': f"解压缩操作只能指定一个源文件，但提供了{len(source_paths)}个"
            }
        
        source_path = source_paths[0]
        
        # 检查源文件是否存在
        if not os.path.exists(source_path):
            return {
                'success': False,
                'message': f"压缩文件 {source_path} 不存在"
            }
        
        # 检查源文件是否是文件而非目录
        if not os.path.isfile(source_path):
            return {
                'success': False,
                'message': f"{source_path} 不是一个文件"
            }
        
        # 确保输出目录存在
        os.makedirs(output_path, exist_ok=True)
        
        try:
            # 根据文件扩展名判断压缩格式
            if format is None:
                ext = os.path.splitext(source_path)[1].lower()
                if ext == '.zip':
                    format = 'zip'
                elif ext == '.tar':
                    format = 'tar'
                elif ext in ('.tar.gz', '.tgz', '.gz'):
                    format = 'gztar'
                elif ext in ('.tar.bz2', '.tbz2', '.bz2'):
                    format = 'bztar'
                elif ext in ('.tar.xz', '.txz', '.xz'):
                    format = 'xztar'
                else:
                    return {
                        'success': False,
                        'message': f"无法根据扩展名确定压缩格式: {source_path}"
                    }
            
            # 使用对应格式解压文件
            if format == 'zip':
                with zipfile.ZipFile(source_path, 'r') as zipf:
                    zipf.extractall(output_path)
            elif format in ('tar', 'gztar', 'bztar', 'xztar'):
                with tarfile.open(source_path, 'r:*') as tarf:
                    tarf.extractall(output_path)
            
            return {
                'success': True,
                'message': f"文件 {source_path} 已解压到 {output_path}",
                'extract_dir': os.path.abspath(output_path),
                'format': format
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"解压缩操作失败: {str(e)}"
            }
    
    else:
        return {
            'success': False,
            'message': f"不支持的操作: {action}"
        }