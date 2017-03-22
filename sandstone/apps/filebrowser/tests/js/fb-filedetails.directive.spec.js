xdescribe('sandstone.filebrowser.fbFileDetails', function() {
  var baseElement = '<div fb-file-details></div>';

  var volumeDetails = {
    available: '11G',
    filepath: '/volume1/',
    size: '18G',
    type: 'volume',
    used: '6.0G',
    used_pct: 36
  };
  var fsDetails = {
    groups: ['testgrp'],
    type: 'filesystem',
    volumes: [volumeDetails]
  };
  var fileDetails = {
    type: 'file',
    filepath: '/volume1/file1',
    dirpath: '/volume1',
    name: 'file1',
    owner: 'testuser',
    group: 'testgrp',
    permissions: 'rwxrw-r--',
    size: '8.8K'
  };
  var dirDetails = {
    type: 'directory',
    filepath: '/volume1',
    dirpath: '/volume1/',
    name: 'volume1',
    owner: 'testuser',
    group: 'testgrp',
    permissions: 'rwxrw-r--',
    size: '4.0K',
    contents: [fileDetails]
  };

  beforeEach(module('sandstone'));
  beforeEach(module('sandstone.templates'));
  beforeEach(module('sandstone.broadcastservice'));
  beforeEach(module('sandstone.filesystemservice'));
  beforeEach(module('sandstone.filebrowser'));

  describe('controller', function() {
    var $compile, $scope, isolateScope, element, FilesystemService, FilebrowserService, BroadcastService, mockResolve;

    beforeEach(inject(function(_$compile_,_$rootScope_,_$q_,_FilesystemService_,_FilebrowserService_,_BroadcastService_) {
      mockResolve = function(data) {
        var deferred = _$q_.defer();
        deferred.resolve(data);
        return deferred.promise;
      };

      FilesystemService = _FilesystemService_;
      FilebrowserService = _FilebrowserService_;
      BroadcastService = _BroadcastService_;
      $compile = _$compile_;
      $scope = _$rootScope_.$new();

      // Called on load
      spyOn(FilesystemService,'getFilesystemDetails').and.callFake(function() {
        return mockResolve(fsDetails);
      });

      element = $compile(baseElement)($scope);
      $scope.$digest();
      isolateScope = element.isolateScope();
    }));

    it('gets filesystem details on load',function() {
      expect(FilesystemService.getFilesystemDetails).toHaveBeenCalled();
    });

    it('watches for selection changes on the scope',function() {});

    it('creates a deep copy of the selected file for editing',function() {});

    it('edit file contains a model for permissions edits',function() {});

    it('editing filename renames the file',function() {});

    it('selecting a new group changes the group',function() {});

    it('editing permissions model changes permissions',function() {});

    it('opening in editor sends signal and changes location',function() {});

    it('duplicates created with proper suffix',function() {});

    it('file moved to location specified by move modal',function() {});

    it('file is deleted and selection is cleared',function() {});

  });

  describe('directive', function() {
    var $compile, $scope, isolateScope, element, FilesystemService, FilebrowserService, BroadcastService, mockResolve;

    var getMatchesFromTpl = function(pattern,tpl) {
      var matches = tpl.match(pattern);
      if (!matches) {
        return [];
      }
      return matches;
    };

    var renderTpl = function(scope,el) {
      var tpl;
      scope.$digest();
      tpl = el.html();
      return tpl;
    };

    beforeEach(inject(function(_$compile_,_$rootScope_,_$q_,_FilesystemService_,_FilebrowserService_,_BroadcastService_) {
      mockResolve = function(data) {
        var deferred = _$q_.defer();
        deferred.resolve(data);
        return deferred.promise;
      };

      FilesystemService = _FilesystemService_;
      FilebrowserService = _FilebrowserService_;
      BroadcastService = _BroadcastService_;
      $compile = _$compile_;
      $scope = _$rootScope_.$new();

      // Called on load
      spyOn(FilebrowserService,'getFilesystem').and.callFake(function() {
        return mockResolve(fsDetails);
      });

      element = $compile(baseElement)($scope);
      $scope.$digest();
      isolateScope = element.isolateScope();
    }));

    it('changes to edit propagate to template',function() {});

    it('group select is populated',function() {});

    it('permissions matrix renders properly',function() {});

  });

});
