# plugin-aws-inven-collector

## Overall Collecting Process Before Refactoring
![aws_before_refactoring_white](https://github.com/Sooyoung98/plugin-aws-inven-collector/assets/79274380/85b9823d-c0fa-406d-8300-15e6054e998e)


* 기존 AWS Collector는 Multithreading 기반으로 각 aws service를 기준으로 region별 수집을 수행하였습니다.
* 수집해온 정보들을 pydantic model을 통해 정형화하여 본래 request의 source인 inventory microservice로 전달하였습니다.
* 이러한 방식은, pydantic model을 통해 정형화하는 과정 자체도 heavy workload를 발생시켰으며, 이로 인해 수집 시간이 길어지는 문제가 발생하였습니다. 

## Overall Collecting Process After Refactoring
![aws_after_refactoring_white](https://github.com/Sooyoung98/plugin-aws-inven-collector/assets/79274380/e057d207-87b3-4c10-b163-a825c7d7ea1c)


* 위에 언급한 문제를 해결함과 동시에 좀 더 세분화된 정보 수집을 실현하기 위해, AWS Collector를 Refactoring하였습니다.
* 기존의 Multithreading 기반의 수집 방식을 Factory Pattern 을 통해 각 Service & Region 별로 수집을 수행하도록 변경하였습니다.
* 또한, 기존에 쓰였던 model 정형화를 하지 않고 raw data를 어느정도 preprocessing하여 전달하는 방식을 채택하여 속도를 높일 것으로 예상됩니다.


## 새로운 수집 단위: Task 

* 이 collector는 old collector와 동일하게 수집명령을 inventory microservice로부터 받지만, 받는 형태는 Task형태로 받게 됩니다.
* Task는 수집을 수행하는데 필요한 정보를 담고 있으며, 아래의 task type들이 존재합니다.
  1. inventory.CloudService
     1. 이 type의 task는 Cloud service들 자체의 정보들을 수집하며, 이 task를 통해 특정 region에 있는 특정 cloud service의 수집이 가능합니다.
  2. inventory.CloudServiceType
     1. 이 type의 task는 각 Cloud service들의 metadata 정보들만을 수집합니다. 이 task를 통해 특정 cloud service의 metadata 정보수집이 가능합니다.
  3. inventory.Region
     1. 이 type의 task는 각 Region들의 정보들만을 수집합니다. 이 task를 통해 특정 region의 정보수집이 가능합니다.
  
    ### Task Code Flow
    * 이러한 task들은 아래의 **code flow**를 따라 생성 및 이용되고 있습니다.
      
      ![task_creation_use_flow](https://github.com/Sooyoung98/plugin-aws-inven-collector/assets/79274380/8e975572-fde2-4e24-a31a-96db7778b97e)

      1. Inventory Microservice에서 AWS Collector내 main.py에 있는 job_get_tasks() 함수를 호출합니다.
      2. job_get_tasks() 함수 내에서는 input을 통해 받은 cloud service이름들이 있거나 region들이 있다면, 해당 input들을 기준으로 inventory.CloudService, inventory.CloudServiceType, inventory.Region task들을 생성합니다.
      3. 생성된 task들을 하나의 list에 담아 다시 Inventory Microservice로 전달합니다.
      4. Inventory Microservice는 전달받은 task들을 이용해 여러 내부 함수들을 걸쳐서 AWS Collector()의 collector_collect()함수를 호출합니다.

## Class Hierarchy (Same for ResourceConnector)
![Factory_white](https://github.com/Sooyoung98/plugin-aws-inven-collector/assets/79274380/610b1f71-83a1-4e14-be42-0b083a9225a8)


* 새로운 AWS Collector는 Factory Pattern을 통해 수집을 진행하는데, 이로 인해 생기는 이점은 새로운 service가 추가되어도 손쉽게 추가 및 적용이 가능해집니다.
* 또한, 하나의 master class로 인해 자식 class 간의 class 중복현상을 방지할 수 있습니다.

## Overall Code Flow Example: Collect CloudTrail (Collecting Cloud Service)
![AWS Refactoring - CloudService Collect Process Final](https://github.com/Sooyoung98/plugin-aws-inven-collector/assets/79274380/6b3f12a4-7c9e-4819-8429-976137b49c24)


* 해당 그림은 CloudTrail을 수집할 때 내부적으로 어떤 flow로 진행되는지를 보여주고 있습니다. 아래의 절차를 따릅니다.
    1. Inventory Microservice에서 inventory.CloudService Task를 통해 AWS collector의 main.py 내 collector_collect() 함수 호출을 하여 수집 명령이 들어옵니다.
    2. 들어온 input 중에 service 이름을 확인하여 ResourceManager의 get_manager_by_service() 를 이용해 해당 service에 맞는 CloudTrailManager class object를 initialize합니다. 
    3. CloudTrailManager class는 ResourceManager의 자식 클래스이므로 ResourceManager의 함수 중 하나인 collect_resources()를 CloudTrailManager를 통해 호출합니다.
    4. collect_resources() 함수 내에서, input으로 들어온 service 이름을 이용하여 ResourceConnector의 get_connector() 를 이용해 해당 service에 맞는 CloudTrailConnector class object를 initialize합니다.
    5. ResourceManager의 collect_cloud_service() 함수를 전에 initialize한 CloudTrailConnector를 통해 호출합니다.
    6. collect_cloud_service() 함수 내에서, CloudTrailManager가 가진 create_cloud_service() 함수를 호출합니다.
    7. create_cloud_service() 함수 내에서, CloudTrailConnector가 가진 get_trails() 함수가 호출되고, 해당 함수의 리턴값를 이용해 CloudTrailManager 내에서 preprocessing을 진행합니다.
    8. 최종적으로, preprocessing이 끝난 자료를 CloudServiceResponse model에 정형화한 후 ResourceResponse model에 정형화하여 Inventory Microservice로 전달합니다.
